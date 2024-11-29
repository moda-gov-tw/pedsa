using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Mvc;
using DeIdWeb_V2.Models;
using DeIdWeb_V2.Infrastructure.Service;
using log4net;
using DeIdWeb_V2.Infrastructure.Reposiotry;
using Microsoft.AspNetCore.Localization;
using Resources;
using Microsoft.AspNetCore.Authentication;
using System.Security.Claims;
using Microsoft.Extensions.Configuration;
using Microsoft.AspNetCore.Authentication.Cookies;
using Microsoft.AspNetCore.Authorization;
using Microsoft.Extensions.Logging;
using System.Security.Principal;
using System.Linq;
using Newtonsoft.Json;
using System.Security.Cryptography;
using System.Text;

using System.Threading;

using Microsoft.AspNetCore.Http;
using System.IO;
using Microsoft.AspNetCore.Hosting;
using DeIdWeb_V2.Filters;
using PETs_Dir.Infrastructure.Service;

namespace DeIdWeb_V2.Controllers
{
    [TypeFilter(typeof(CultureFilter))]
    [ResponseCache(NoStore = true)]
    public class HomeController : BaseController
    {
        private readonly ILogger<HomeController> _logger; //定義日誌物件
        //private readonly IStringLocalizer<HomeController> _localizer;
        
        public SystemLog_Service syslog_service = new SystemLog_Service();
        public Project_Service proService = new Project_Service();
        public HttpHelper httphelp = new HttpHelper();
        public GenSettingRandomData genRandim = new GenSettingRandomData();
        private ILog log = LogManager.GetLogger(Startup.repository.Name, typeof(HomeController));
        private readonly ILocalizer _localizer;
        private readonly IConfiguration config;
        private readonly IHttpContextAccessor _httpContextAccessor;
        private readonly IWebHostEnvironment _hostingEnvironment;
        public HomeController(ILocalizer localizer, IConfiguration Config, ILogger<HomeController> logger, IHttpContextAccessor httpContextAccessor, IWebHostEnvironment hostingEnvironment)
        {
            _localizer = localizer;
            logger = logger; //初始化日誌物件
            this.config = Config;
            _httpContextAccessor = httpContextAccessor;
            _hostingEnvironment = hostingEnvironment;
            
        }

        private static Encoding DetectEncoding(byte[] buffer)
        {
            if (buffer.Length >= 3 && buffer[0] == 0xEF && buffer[1] == 0xBB && buffer[2] == 0xBF)
            {
                return Encoding.UTF8;
            }
            else if (buffer.Length >= 4 && buffer[0] == 0xFF && buffer[1] == 0xFE && buffer[2] == 0x00 && buffer[3] == 0x00)
            {
                return Encoding.UTF32;
            }
            else if (buffer.Length >= 4 && buffer[0] == 0x00 && buffer[1] == 0x00 && buffer[2] == 0xFE && buffer[3] == 0xFF)
            {
                return new UTF32Encoding(true, true);
            }
            else if (buffer.Length >= 2 && buffer[0] == 0xFE && buffer[1] == 0xFF)
            {
                return Encoding.BigEndianUnicode;
            }
            else if (buffer.Length >= 2 && buffer[0] == 0xFF && buffer[1] == 0xFE)
            {
                return Encoding.Unicode;
            }
            else
            {
                return Encoding.Default; // 預設編碼
            }
        }
        static string DecodeUtf8(string utf8String)
        {
            byte[] utf8Bytes = Encoding.UTF8.GetBytes(utf8String);
            string decodedString = Encoding.UTF8.GetString(utf8Bytes);
            return decodedString;
        }
        [HttpPost]
        
        public async Task<IActionResult> Upload(IFormFile file)
        {
            string filename = "";
            string project_cert = "";
            string delimiter = "";
            //string originalData = "皜祈岫鞈���";

            //// 將 UTF-8 編碼的字串轉換為 Unicode 字串
            //string decodedData = DecodeUtf8(originalData);

            //var cht_name = "";
            if (file == null || file.Length == 0)
            {
                return Content("檔案並未選擇!");
            }

            // 檢查檔案大小是否超出限制
            if (file.Length > 1024 * 1024 * 1024) // 1GB
            {
                return Content("檔案大小超出限制!");
            }
            try
            {

                using (var memoryStream = new MemoryStream())
                {
                    file.CopyTo(memoryStream);
                    byte[] buffer = memoryStream.ToArray();

                    Encoding detectedEncoding = DetectEncoding(buffer);
                    //if (detectedEncoding != Encoding.UTF8)
                    //{
                    //    return Content("檔案格式編碼不正確!");
                    //}

                    // 在這裡可以繼續處理你的上傳邏輯
                    // ...
                    filename = Request.Form["filename"];
                    project_cert = Request.Form["project_cert"];
                    delimiter = Request.Form["delimiter"];
                    string uploadsfolder = "uploads";
                    var uploadDir = Path.Combine(_hostingEnvironment.WebRootPath, uploadsfolder);
                    log.Info($"--------uploadDir :{uploadDir}");
                    log.Info("uploadDir :" + uploadDir);

                    if (!Directory.Exists(uploadDir))
                    {
                        Directory.CreateDirectory(uploadDir);
                    }
                  
                    var filePath = Path.Combine(uploadDir, file.FileName);
                  
                    using (var stream = new FileStream(filePath, FileMode.Create))
                    {
                        await file.CopyToAsync(stream);
                    }
                    log.Info("Login User : -3.5");
                    //上傳完畢，寫入表頭
                    string fileheader = Request.Form["fireheader"];

                    //replace header ""
                    fileheader = fileheader.Replace("\"", "");
                    fileheader = fileheader.Replace("\\r\\n", "");
                    // var header_arr = fireheader.Split(',');
                  //  sessionStorage.setItem('fileheader', fileheader);

                    return Ok();
                   //return RedirectToAction("DirSetting", new { fileheader = fileheader, file_key = file_key});

                }

            }
            catch (Exception ex)
            {
                log.Info("Login User : -3.55");
                var logstr = "資料上傳 檔案 : " + filename + " 失敗 Exception " + ex.Message;
                log.Info(logstr);
                
                return Content("檔案上傳失敗!");
            }
        }
        static string DecodeBig5(string big5String)
        {
            // 註冊 Big5 編碼提供者
            Encoding.RegisterProvider(CodePagesEncodingProvider.Instance);

            // 使用 "big5" 作為編碼名稱
            Encoding big5 = Encoding.GetEncoding("big5");

           
            // 將 Big5 編碼的字串轉換為 byte[]
            byte[] big5Bytes = big5.GetBytes(big5String);

            // 將 byte[] 轉換為 Unicode 字串
            string decodedString = Encoding.Unicode.GetString(big5Bytes);

            return decodedString;
        }

        public IActionResult FileUploadState()
        {
            
            var lstdepthis = proService.getserveripuploadfilelist();
            var final_memlist = "";
            string jsonData = JsonConvert.SerializeObject(lstdepthis);
            ViewData["app_list"] = jsonData;
            return View();
        }

            public IActionResult DirSetting(string filename,string fileheader, string project_cert,string delimiter)
        {
            ViewData["filename"] = "";
            ViewData["upload_header"] = "";
            ViewData["fileheader"] = "";
            ViewData["delimiter"] = delimiter;
            ViewData["project_cert"] = project_cert;
            string originalData = "皜祈岫鞈���";

            // 將 UTF-8 編碼的字串轉換為 Unicode 字串
            string decodedData = DecodeBig5(originalData);
            //string a = "\"A\",\"B\",\"C\"";
           
            //var filename = "";
            var upload_header = "";
            try
            {

                if (!string.IsNullOrEmpty(filename))
                {
                 
                    ViewData["filename"] = filename;
                }

                if (!string.IsNullOrEmpty(fileheader))
                {
                    if (fileheader.StartsWith("\"") && fileheader.EndsWith("\""))
                    {
                        string replacedString = fileheader.Replace("\",\"", ",").Trim('"');
                        Console.WriteLine(replacedString);  // 输出： A|B|C
                        ViewData["delimiter"] = ",";
                        ViewData["upload_header"] = replacedString;
                    }
                    else
                    {
                        ViewData["delimiter"] = ",";
                        ViewData["upload_header"] = fileheader;
                    }
                   
                }
            }
            catch (Exception ex)
            {
                log.Error(" DirSetting Exception : " + ex.Message);
            }
            return View();
        }

        public IActionResult StepGroup(string proj_id, string project_name, string project_cht)
        {
            return View();
        }
            public IActionResult StepUpload(string proj_id, string project_name, string project_cht)
        {

            var memberAcc = "";
            var memberId = "";
            var isAdmin = "";
            var isChange = 1;
            var cht_name = "";
            string selectname = _localizer.Text.select;
            ViewData["ProjectId"] = proj_id;
            ViewData["ProjectName"] = project_name;
            ViewData["project_cht"] = project_cht;
            ViewData["memberId"] = memberId;
            ViewData["memberAcc"] = memberAcc;
            try
            {
               // lst = ps_Service.SelectProjSampleTablebyId(proj_id);

            }
            catch (Exception ex)
            {
                log.Error(" StepUpload Exception :" + ex.Message);
               
                var logstr = "StepUpload 上傳資料錯誤  " + ex.Message;
                log.Info(logstr);
               
            }
            return View();
        }

        private void DeleteAllCookies()
        {
            var context = _httpContextAccessor.HttpContext;
            var cookies = context.Request.Cookies;

            foreach (var key in cookies.Keys)
            {
                context.Response.Cookies.Delete(key);
            }
        }

        public IActionResult Error()
        {
            return View(new ErrorViewModel { RequestId = Activity.Current?.Id ?? HttpContext.TraceIdentifier });
        }
    }
}
