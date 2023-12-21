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

namespace DeIdWeb_V2.Controllers
{
    [TypeFilter(typeof(CultureFilter))]
    [ResponseCache(NoStore = true)]
    public class HomeController : BaseController
    {
        private readonly ILogger<HomeController> _logger; //定義日誌物件
        //private readonly IStringLocalizer<HomeController> _localizer;
        
        public SystemLog_Service syslog_service = new SystemLog_Service();
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

        [HttpPost]
        
        public async Task<IActionResult> Upload(IFormFile file)
        {
            string filename = "";
            string file_key = "";
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
                    file_key = Request.Form["firekey"];
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

        public IActionResult DirSetting(string filename,string fileheader, string file_key)
        {
            ViewData["filename"] = "";
            ViewData["upload_header"] = "";
            ViewData["fileheader"] = "";
            ViewData["file_key"] = file_key;
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
                    ViewData["upload_header"] = fileheader;
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
