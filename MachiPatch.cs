using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Drawing;
using System.IO;
using System.Text;
using System.Threading.Tasks;
using System.Web.Script.Serialization;
using System.Windows.Forms;

public sealed class MachiPatch : Form {
    readonly string root=AppDomain.CurrentDomain.BaseDirectory;
    TextBox source=new TextBox(), output=new TextBox(), log=new TextBox();
    Button chooseSource=new Button(), chooseOutput=new Button(), apply=new Button(), openFolder=new Button(), copy=new Button();
    Label status=new Label(); ProgressBar progress=new ProgressBar();
    bool busy=false;
    public MachiPatch(string iso) {
        Text="거리 · 운명의 교차점 특별편 — 한글패치 R42";
        Font=new Font("맑은 고딕",10F); ClientSize=new Size(730,555);
        MinimumSize=new Size(746,594); FormBorderStyle=FormBorderStyle.FixedSingle; MaximizeBox=false;
        StartPosition=FormStartPosition.CenterScreen; BackColor=Color.FromArgb(247,249,252);
        var title=new Label{Text="거리 · 운명의 교차점 특별편",Font=new Font("맑은 고딕",18F,FontStyle.Bold),AutoSize=true,Location=new Point(24,20)};
        Controls.Add(title);
        AddLabel("R42  |  일본판 원본 ISO를 선택하면 한글 CSO를 만듭니다.",24,64,680,26);
        AddLabel("1. 원본 ISO",24,105,200,24);
        source.SetBounds(24,133,560,28);source.ReadOnly=true;Controls.Add(source);
        chooseSource.Text="ISO 선택";chooseSource.SetBounds(596,132,108,32);chooseSource.Click+=(s,e)=>SelectSource();Controls.Add(chooseSource);
        AddLabel("2. 결과 저장 위치",24,182,250,24);
        output.SetBounds(24,210,560,28);output.ReadOnly=true;output.Text=Path.Combine(root,"Machi_R42_Korean.cso");Controls.Add(output);
        chooseOutput.Text="저장 위치";chooseOutput.SetBounds(596,209,108,32);chooseOutput.Click+=(s,e)=>SelectOutput();Controls.Add(chooseOutput);
        apply.Text="3. 한글패치 적용 시작";apply.SetBounds(24,262,400,42);apply.BackColor=Color.FromArgb(30,92,170);apply.ForeColor=Color.White;apply.FlatStyle=FlatStyle.Flat;
        apply.Click+=async(s,e)=>await RunPatch();Controls.Add(apply);
        openFolder.Text="결과 폴더 열기";openFolder.SetBounds(440,262,264,42);openFolder.Enabled=false;openFolder.Click+=(s,e)=>Process.Start("explorer.exe",Quote(Path.GetDirectoryName(output.Text)));Controls.Add(openFolder);
        status.SetBounds(24,320,680,25);status.Text="원본 ISO는 변경하지 않습니다. 여유 공간 5GB 이상을 권장합니다.";Controls.Add(status);
        progress.SetBounds(24,351,680,18);Controls.Add(progress);
        log.SetBounds(24,384,680,110);log.Multiline=true;log.ReadOnly=true;log.ScrollBars=ScrollBars.Vertical;log.BackColor=Color.White;Controls.Add(log);
        copy.Text="결과 메시지 복사";copy.SetBounds(520,508,184,30);copy.Click+=(s,e)=>{if(log.Text.Length>0)Clipboard.SetText(log.Text);};Controls.Add(copy);
        AddLabel("ISO를 창 위에 끌어다 놓아도 선택할 수 있습니다.",24,514,470,25);
        AllowDrop=true;DragEnter+=(s,e)=>{if(!busy&&e.Data.GetDataPresent(DataFormats.FileDrop))e.Effect=DragDropEffects.Copy;};
        DragDrop+=(s,e)=>{var files=(string[])e.Data.GetData(DataFormats.FileDrop);if(!busy&&files.Length==1)source.Text=files[0];};
        FormClosing+=(s,e)=>{if(busy){e.Cancel=true;status.Text="적용 중입니다. 결과 검증이 끝날 때까지 기다려 주세요.";}};
        if(!String.IsNullOrWhiteSpace(iso))source.Text=Path.GetFullPath(iso);
    }
    void AddLabel(string text,int x,int y,int w,int h){Controls.Add(new Label{Text=text,Location=new Point(x,y),Size=new Size(w,h)});}
    void SelectSource(){using(var d=new OpenFileDialog{Title="일본판 원본 ISO 선택",Filter="PSP 원본 ISO (*.iso)|*.iso|모든 파일 (*.*)|*.*",CheckFileExists=true}){if(d.ShowDialog(this)==DialogResult.OK)source.Text=d.FileName;}}
    void SelectOutput(){using(var d=new SaveFileDialog{Title="한글 CSO 저장 위치",Filter="PSP CSO (*.cso)|*.cso",FileName="Machi_R42_Korean.cso",OverwritePrompt=false,AddExtension=true}){if(d.ShowDialog(this)==DialogResult.OK)output.Text=d.FileName;}}
    public static string Quote(string text){return "\""+text.Replace("\"","\\\"")+"\"";}
    string FindPython(){
        string bundled=Path.Combine(root,"runtime","python.exe");
        if(File.Exists(bundled))return bundled;
        var candidates=new List<string>{Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData),"Programs","Python","Python311","python.exe"),Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.ProgramFiles),"Python311","python.exe")};
        foreach(string dir in (Environment.GetEnvironmentVariable("PATH")??"").Split(';')){
            try{if(!String.IsNullOrWhiteSpace(dir)&&dir.IndexOf("WindowsApps",StringComparison.OrdinalIgnoreCase)<0)candidates.Add(Path.Combine(dir.Trim('"'),"python.exe"));}catch{}
        }
        foreach(string candidate in candidates)if(File.Exists(candidate))return candidate;
        return null;
    }
    async Task RunPatch(){
        if(busy)return;
        if(!File.Exists(source.Text)){status.Text="먼저 원본 ISO를 선택해 주세요.";SelectSource();return;}
        var python=FindPython();
        if(python==null||!File.Exists(Path.Combine(root,"apply_patch.py"))||!File.Exists(Path.Combine(root,"patch_core.py"))){
            status.Text="실행에 필요한 파일이 없습니다.";log.Text="간편 적용판 ZIP 전체를 새 폴더에 풀어 주세요. MachiPatch.exe만 따로 옮기면 실행되지 않습니다. runtime 폴더도 함께 있어야 합니다.";return;
        }
        busy=true;apply.Enabled=chooseSource.Enabled=chooseOutput.Enabled=false;openFolder.Enabled=false;progress.Value=0;log.Clear();
        status.Text="원본을 확인하고 있습니다…";
        var info=MakeStartInfo(python,root,source.Text,output.Text);
        bool completed=false;string failure=null;
        var parser=new JavaScriptSerializer();
        try{
            int code=await Task.Run(()=>{
                using(var p=new Process{StartInfo=info}){
                    p.Start();var errorTask=p.StandardError.ReadToEndAsync();
                    string line;
                    while((line=p.StandardOutput.ReadLine())!=null){
                        try{
                            var row=parser.Deserialize<Dictionary<string,object>>(line);
                            Invoke((Action)(()=>{
                                string kind=Convert.ToString(row["event"]);
                                if(kind=="rebuild"){
                                    int value=(int)(100L*Convert.ToInt64(row["blocks"])/Convert.ToInt64(row["total_blocks"]));
                                    progress.Value=Math.Min(99,value);status.Text="한글패치를 적용하고 있습니다… "+value+"%";
                                }else if(kind=="phase")status.Text=Convert.ToString(row["message"]);
                                else if(kind=="error"){
                                    failure="["+Convert.ToString(row["code"])+"] "+Convert.ToString(row["message"]);log.AppendText(failure+Environment.NewLine);
                                }else if(kind=="complete"){
                                    completed=true;progress.Value=100;status.Text=Convert.ToString(row["message"]);log.AppendText(status.Text+Environment.NewLine+"파일: "+Path.GetFileName(output.Text)+Environment.NewLine+"SHA-256: "+Convert.ToString(row["sha256"])+Environment.NewLine);
                                }
                            }));
                        }catch{ /* Do not expose runtime tracebacks or private paths in shareable results. */ }
                    }
                    p.WaitForExit();errorTask.GetAwaiter().GetResult();return p.ExitCode;
                }
            });
            if(code==0&&completed){openFolder.Enabled=true;}
            else{status.Text="적용을 완료하지 못했습니다. 아래 안내를 확인해 주세요.";if(failure==null)log.AppendText("[START] 실행 환경을 불러오지 못했습니다. 간편 적용판 ZIP을 새 폴더에 모두 풀고 실행해 주세요."+Environment.NewLine);}
        }catch{status.Text="적용 프로그램을 실행하지 못했습니다.";log.AppendText("[START] runtime 폴더가 포함된 간편 적용판인지 확인해 주세요. 이 프로그램은 Windows 10/11 64비트용입니다.");}
        finally{busy=false;apply.Enabled=chooseSource.Enabled=chooseOutput.Enabled=true;}
    }
    public static ProcessStartInfo MakeStartInfo(string python,string root,string iso,string output){
        return new ProcessStartInfo(python,"-I -B -X utf8 "+Quote(Path.Combine(root,"apply_patch.py"))+" --source "+Quote(iso)+" --output "+Quote(output)){
            WorkingDirectory=root,UseShellExecute=false,CreateNoWindow=true,RedirectStandardOutput=true,RedirectStandardError=true,StandardOutputEncoding=Encoding.UTF8,StandardErrorEncoding=Encoding.UTF8
        };
    }
    [STAThread] public static int Main(string[] args){
        if(args.Length==3&&args[0]=="--verify-ui"){
            Application.EnableVisualStyles();Application.SetCompatibleTextRenderingDefault(false);
            int result=1;
            using(var form=new MachiPatch(args[1])){
                form.output.Text=args[2];var handle=form.Handle;
                EventHandler test=null;
                test=async(s,e)=>{
                    Application.Idle-=test;
                    await form.RunPatch();
                    result=(!form.busy&&form.openFolder.Enabled&&form.progress.Value==100)?0:1;
                    File.WriteAllText(Path.Combine(form.root,"ui-verification.json"),new JavaScriptSerializer().Serialize(new {passed=result==0,progress=form.progress.Value,busy=form.busy,canOpenOutput=form.openFolder.Enabled,message=form.log.Text}),new UTF8Encoding(false));
                    Application.ExitThread();
                };
                Application.Idle+=test;Application.Run();
            }
            return result;
        }
        if(args.Length==2&&args[0]=="--render-preview"){
            Application.EnableVisualStyles();Application.SetCompatibleTextRenderingDefault(false);
            using(var form=new MachiPatch(null)){
                form.source.Text="original.iso";form.output.Text="Machi_R42_Korean.cso";
                form.CreateControl();
                using(var bitmap=new Bitmap(form.ClientSize.Width,form.ClientSize.Height)){
                    using(var g=Graphics.FromImage(bitmap)){
                        g.Clear(form.BackColor);
                        foreach(Control control in form.Controls){using(var part=new Bitmap(control.Width,control.Height)){control.DrawToBitmap(part,new Rectangle(0,0,control.Width,control.Height));g.DrawImageUnscaled(part,control.Location);}}
                    }
                    bitmap.Save(args[1],System.Drawing.Imaging.ImageFormat.Png);
                }
            }
            return 0;
        }
        // Automated application-path check; uses the exact same child-process configuration as the form.
        if(args.Length==3&&args[0]=="--verify-launch"){
            string root=AppDomain.CurrentDomain.BaseDirectory;
            using(var p=new Process{StartInfo=MakeStartInfo(Path.Combine(root,"runtime","python.exe"),root,args[1],args[2])}){
                p.Start();var stdout=p.StandardOutput.ReadToEndAsync();var stderr=p.StandardError.ReadToEndAsync();p.WaitForExit();
                File.WriteAllText(Path.Combine(root,"launcher-verification.jsonl"),stdout.Result,new UTF8Encoding(false));return p.ExitCode;
            }
        }
        Application.EnableVisualStyles();Application.SetCompatibleTextRenderingDefault(false);
        Application.Run(new MachiPatch(args.Length>0?args[0]:null));return 0;
    }
}
