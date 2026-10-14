"""Machi R42 application helper, installer revision 1. No third-party modules."""
from pathlib import Path
import argparse, hashlib, importlib.util, json, os, struct, sys, time, uuid, zipfile, zlib

ROOT=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('machi_patch_core',ROOT/'patch_core.py')
core=importlib.util.module_from_spec(spec)
spec.loader.exec_module(core)

def emit(event,**values):
    print(json.dumps(dict(event=event,**values),ensure_ascii=False),flush=True)

class ApplyError(Exception):
    def __init__(self,code,message):
        super().__init__(message);self.code=code

def check_runtime():
    if sys.version_info[:2] < (3,11) or struct.calcsize('P') != 8 or zlib.ZLIB_RUNTIME_VERSION != '1.3.1':
        raise ApplyError('RUNTIME','이 Python 환경은 지원하지 않습니다. 간편 적용판 ZIP을 새 폴더에 모두 풀고 MachiPatch.exe를 실행해 주세요.')

ERRORS={
 'Original ISO size does not match.':('ISO_SIZE','지원하는 일본판 원본 ISO와 파일 크기가 다릅니다. ULJM-05111 일본판 ISO(1,542,422,528바이트)를 선택해 주세요. CSO나 이미 패치된 파일은 사용할 수 없습니다.'),
 'Original ISO SHA256 does not match.':('ISO_HASH','파일 크기는 맞지만 원본 내용이 다릅니다. 지원 원본의 SHA-256을 설명서에서 확인해 주세요. 파일명만 바꾸어서는 적용할 수 없습니다.'),
 'Insufficient free space.':('SPACE','결과를 저장할 드라이브에 공간이 부족합니다. 여유 공간 5GB 이상을 확보하거나 다른 저장 위치를 선택해 주세요.'),
 'CISO index mismatch; compression runtime may differ.':('RUNTIME','압축 결과가 기준과 다릅니다. ZIP에 포함된 runtime 폴더를 그대로 두고 MachiPatch.exe로 다시 실행해 주세요.'),
 'Output SHA256 mismatch.':('OUTPUT_HASH','완성 파일의 검증에 실패했습니다. 불완전한 결과는 제거했습니다. 배포 ZIP을 다시 받아 새 폴더에서 적용해 주세요.'),
}

def apply(source,patch,output):
    check_runtime()
    source,patch,output=(Path(p).resolve() for p in (source,patch,output))
    if not patch.is_file():
        raise ApplyError('PATCH_MISSING','패치 데이터가 없습니다. Source code가 아닌 Machi_PSP_Korean_R42_Easy.zip을 받고 ZIP 전체를 풀어 주세요. 내부의 .patch.zip은 풀지 않고 그대로 둡니다.')
    if not source.is_file():
        raise ApplyError('ISO_MISSING','선택한 ISO 파일을 찾을 수 없습니다. 압축파일 안이 아닌 실제 폴더에 있는 원본 ISO를 다시 선택해 주세요.')
    if len({source,patch,output})!=3:
        raise ApplyError('SAME_PATH','원본 파일과 결과 파일은 서로 다른 이름이어야 합니다.')
    if not output.parent.is_dir():
        raise ApplyError('OUTPUT_FOLDER','저장할 폴더가 없습니다. 저장 위치를 다시 선택해 주세요.')
    if output.exists():
        if output.is_file() and output.stat().st_size==1712404852:
            emit('phase',message='기존 결과 파일을 확인하고 있습니다.')
            if core.digest(output)==core.TARGET_SHA:
                return dict(status='ALREADY_COMPLETE',sha256=core.TARGET_SHA,bytes=output.stat().st_size)
        raise ApplyError('OUTPUT_EXISTS','같은 이름의 파일이 이미 있습니다. 파일은 덮어쓰지 않았습니다. 저장 위치에서 다른 이름을 지정해 주세요. 예전에 실패한 파일이 남아 있을 수도 있습니다.')
    stage=output.with_name(output.name+'.partial-'+uuid.uuid4().hex)
    started=time.monotonic()
    try:
        emit('phase',message='원본 ISO를 검사한 뒤 패치를 적용합니다.')
        result=core.rebuild(source,patch,stage)
        emit('phase',message='검증을 통과했습니다. 결과 파일을 저장합니다.')
        if os.name=='nt':
            os.rename(stage,output)  # Windows refuses to replace an existing destination.
        else:
            os.link(stage,output);stage.unlink()
        result.pop('output',None)
        result['elapsed_seconds']=round(time.monotonic()-started,1)
        return result
    finally:
        if stage.exists():stage.unlink()

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source');parser.add_argument('--patch',default=str(ROOT/'Machi_ORIGINAL_JP_to_R42.patch.zip'))
    parser.add_argument('--output');parser.add_argument('--runtime-check',action='store_true')
    args=parser.parse_args()
    try:
        if args.runtime_check:
            check_runtime();emit('runtime',status='OK',python=sys.version.split()[0],zlib=zlib.ZLIB_RUNTIME_VERSION);return 0
        if not args.source or not args.output:
            raise ApplyError('ARGUMENT','MachiPatch.exe를 더블클릭하여 ISO를 선택해 주세요. 명령줄에서는 --source와 --output을 지정합니다.')
        result=apply(args.source,args.patch,args.output)
        message='이미 정상적인 R42 파일이 있습니다.' if result['status']=='ALREADY_COMPLETE' else '한글패치 적용과 결과 검증이 완료되었습니다.'
        emit('complete',message=message,**result)
        return 0
    except ApplyError as e:emit('error',code=e.code,message=str(e))
    except ValueError as e:
        code,message=ERRORS.get(str(e),('PATCH_DATA','패치 데이터 검증에 실패했습니다. 배포 ZIP을 다시 받고 새 폴더에 모두 풀어 주세요.'))
        emit('error',code=code,message=message)
    except PermissionError:emit('error',code='PERMISSION',message='파일을 읽거나 저장할 권한이 없습니다. 문서 또는 다운로드 폴더 등 쓰기 가능한 위치를 선택하고, 다른 프로그램이 결과 파일을 사용 중인지 확인해 주세요.')
    except FileExistsError:emit('error',code='OUTPUT_EXISTS',message='같은 이름의 결과 파일이 생겨 저장을 중단했습니다. 다른 파일명을 선택해 주세요.')
    except (zipfile.BadZipFile,EOFError,zlib.error):emit('error',code='PATCH_ZIP',message='패치 압축파일이 손상되었습니다. 배포 ZIP을 다시 받아 새 폴더에 모두 풀어 주세요.')
    except OSError as e:emit('error',code='FILE_IO',message='파일 읽기·저장 중 오류가 발생했습니다. 디스크 공간, 저장 권한, 외장 드라이브 연결을 확인해 주세요.',system_error=e.errno)
    except KeyboardInterrupt:emit('error',code='CANCELLED',message='적용을 중단했습니다. 원본 ISO는 변경하지 않았습니다.')
    except Exception:emit('error',code='UNEXPECTED',message='예상하지 못한 오류입니다. 배포 ZIP을 새 폴더에 다시 풀고 실행해 주세요.')
    return 1

if __name__=='__main__':
    raise SystemExit(main())
