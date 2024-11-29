using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Net.Http;
using System.Runtime.CompilerServices;
using System.Security.Cryptography;
using System.Text;
using System.Threading.Tasks;
using DeIdWeb_V2.Infrastructure.Reposiotry;
using DeIdWeb_V2.Infrastructure.Service;
using DeIdWeb_V2.Models;
using DinkToPdf;
using DinkToPdf.Contracts;
using log4net;
using Microsoft.AspNetCore.Hosting;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Localization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Extensions.Configuration;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;
using PETs_Dir.Infrastructure.Service;
using Resources;

namespace DeIdWeb_V2.Controllers
{
    
    [Produces("application/json")]
    [Route("api/WebAPI")]
    public class WebAPIController : Controller
    {
        public Project_Service proService = new Project_Service();
        public SystemLog_Service syslog_service = new SystemLog_Service();
        public HttpHelper httphelper = new HttpHelper();
        public GetGenJsonRep genJsonRp = new GetGenJsonRep();
        private ILog log = LogManager.GetLogger(Startup.repository.Name, typeof(WebAPIController));
        private readonly ILocalizer _localizer;
        private readonly IConverter _convert;
        IWebHostEnvironment webHostEnvironment;

        private readonly IConfiguration _configuration;
        public WebAPIController(ILocalizer localizer, IConverter convert, IConfiguration configuration, IWebHostEnvironment environment)
        {
            _localizer = localizer;
            _convert = convert;
            webHostEnvironment = environment;
            _configuration = configuration;
        }


        private string GetQiSelectName(string selectvalue)
        {
            string getQiSelectName = "";
            switch (selectvalue)
            {
                case "請選擇":
                    getQiSelectName = "請選擇";
                    break;
                case "0":
                    getQiSelectName = "請選擇";
                    break;
                case "1":
                    getQiSelectName = "地址";
                    break;
                case "2":
                    getQiSelectName = "日期";
                    break;
                case "3":
                    getQiSelectName = "擷取字串";
                    break;
                case "4":
                    getQiSelectName = "數字位數";
                    break;
                case "5":
                    getQiSelectName = "數字區間(年齡)";
                    break;
                case "6":
                    getQiSelectName = "數字區間(金額)";
                    break;
                case "7":
                    getQiSelectName = "自訂";
                    break;
                case "8":
                    getQiSelectName = "Hash";
                    break;
                case "9":
                    getQiSelectName = "離群值處理";
                    break;
            }
            return getQiSelectName;
        }


        public string GetClientIpAddress(HttpContext httpContext)
        {
            // Check for X-Forwarded-For header
            var xForwardedForHeader = httpContext.Request.Headers["X-Forwarded-For"].FirstOrDefault();
                log.Info("xForwardedForHeader : " + xForwardedForHeader);

            if (!string.IsNullOrEmpty(xForwardedForHeader))
            {
                // The X-Forwarded-For header can contain multiple IP addresses, split by comma.
                // The first one is the original client IP.
                var clientIp = xForwardedForHeader.Split(',').FirstOrDefault();
                return clientIp;
            }

            // If X-Forwarded-For header is not present, fallback to RemoteIpAddress
            var remoteIpAddress = httpContext.Connection.RemoteIpAddress?.ToString();
            return remoteIpAddress;
        }

        private string GetQiSelectNameLevel2(string selectvalue, string selectlevel2)
        {
            string getQiSelectName = "";
            switch (selectvalue)
            {
                case "請選擇":
                    getQiSelectName = "請選擇";
                    break;
                case "0":
                    getQiSelectName = "請選擇";
                    break;
                case "1":
                    getQiSelectName = "地址";
                    break;
                case "2":
                    getQiSelectName = "日期";
                    break;
                case "3":
                    getQiSelectName = "擷取字串";
                    break;
                case "4":
                    getQiSelectName = "數字位數";
                    break;
                case "5":
                    getQiSelectName = "數字區間(年齡)";
                    break;
                case "6":
                    getQiSelectName = "數字區間(金額)";
                    break;
                case "7":
                    getQiSelectName = "自訂";
                    break;
                case "8":
                    getQiSelectName = "Hash";
                    break;
                case "9":
                    getQiSelectName = "離群值處理";
                    break;
            }
            return getQiSelectName;
        }

        [HttpGet("GetNotificationData")]
        public string GetNotificationData()
        {
            var returnstring = "";
            try
            {
                string clientIpAddress = _configuration["ConnIP:IP"]; //GetClientIpAddress(HttpContext);
                log.Info("clientIpAddress : " + clientIpAddress);

                var lstupfile = proService.getserveripuploadfile(clientIpAddress);
                if (lstupfile.Count > 0)
                {

                    for (int i = 0; i < lstupfile.Count; i++)
                    {
                        var item = lstupfile[i];
                        if (!string.IsNullOrEmpty(item.dataset_name))
                        {
                            returnstring += item.dataset_name;
                            if (i < lstupfile.Count - 1)
                            {
                                returnstring += ",";
                            }
                        }
                    }

                }
                else
                {
                    returnstring = "0";
                }
                return returnstring;
            }
            catch (Exception ex)
            {
                log.Error("GetNotificationData : " + ex.Message.ToString());
                return "Error";
            }
            
        }

            [HttpGet("CheckDirtoImport")]
        public int CheckDirtoImport(string filename, string project_cert, string aes_col, string hash_col)
        {
            try
            {
                var logstr = "直接識別處理 : " + aes_col;
                var logstr_hash = "直接識別處理 : " + hash_col;
                var logstr_project_cert = "project_cert : " + project_cert;
                log.Info("AES 直接識別處理 : " + aes_col);
                log.Info("Hash 直接識別處理 : " + hash_col);
                log.Info("project_cert 直接識別處理 : " + project_cert);
                string filenameWithoutExtension = "";

                if (!string.IsNullOrEmpty(filename))
                {
                    filenameWithoutExtension = Path.GetFileNameWithoutExtension(filename);

                }

                if (string.IsNullOrEmpty(hash_col))
                {
                    hash_col = "";

                }

                if (string.IsNullOrEmpty(aes_col))
                {
                    aes_col = "";
                }
                //call api 
                string clientIpAddress = _configuration["ConnIP:IP"]; //GetClientIpAddress(HttpContext);

                HashKeyModel keymodel = new HashKeyModel
                {
                    aes_col = aes_col,
                    mac_col = hash_col,
                    hash_table_name = filenameWithoutExtension,
                    identifier = project_cert,
                    sep = ",",
                    service_ip = clientIpAddress
                };
                //HashKeyModel keymodel = new HashKeyModel
                //{
                //    aes_col = "ID",
                //    mac_col = "",
                //    hash_table_name = "TP_3000_v2",
                //    identifier = "FNFO6",
                //    sep = ",",
                //    service_ip= "35.194.150.235"
                //};

                string strkeymodel = JsonHelper.SerializeObject(keymodel);
                log.Info("Enc_func Json   String " + strkeymodel);

               //var apirestult = HttpHelper.PostUrl ("direct_enc_async", strkeymodel);
                var apirestult = HttpHelper.PostUrl ("direct_enc_identifier_async", strkeymodel);



                //var apirestult = HttpHelper.PostUrl(enc_api_func, strkeymodel);
                log.Info("Enc_func Json  Return String " + apirestult);
                if (apirestult != "")
                {
                    JObject apidecode = JObject.Parse(apirestult);
                    string apistatus = apidecode["status"].ToString();
                    if (apistatus != "")
                    {
                        if (apistatus != "1")
                            return -1;
                    }
                }
            }
            catch (Exception ex)
            {
                log.Error("CheckDirtoImport Exception :" + ex.Message);
               
                return -1;
            }
            return 1;
        }



        [HttpGet("check_key")]
        public bool check_key(string key_num)
        {
            bool ischeck= false;
            try
            {
                
                log.Info("直接識別處理 個人識別代碼 : " + key_num);
              
                //call api 
                string clientIpAddress = _configuration["ConnIP:IP"]; //GetClientIpAddress(HttpContext);

                check_keynum keymodel = new check_keynum
                {
                    identifier = key_num
                };
                //HashKeyModel keymodel = new HashKeyModel
                //{
                //    aes_col = "Education",
                //    mac_col = "Name,Zipcode",
                //    hash_table_name = "test_7",
                //    enc_key = "9787799D461C5CFE166AF12E25C5A7371B14631A2CA93AB03C9EB0D5710775B2",
                //    sep = ","
                //};

                string strkeymodel = JsonHelper.SerializeObject(keymodel);
                log.Info("check_identifier_async Json   String " + strkeymodel);

                var apirestult = HttpHelper.PostUrl("check_identifier_async ", strkeymodel);



                //var apirestult = HttpHelper.PostUrl(enc_api_func, strkeymodel);
                log.Info("check_identifier_async Json  Return String " + apirestult);
                if (apirestult != "")
                {
                    JObject apidecode = JObject.Parse(apirestult);
                    string apistatus = apidecode["status"].ToString();
                    if (apistatus != "")
                    {
                        if(apistatus=="1")
                        {
                            string check = apidecode["check"].ToString();
                            if(check !="")
                            {
                                if (check == "yes")
                                {
                                    log.Info("check_identifier_async Json   return true");

                                    ischeck= true;
                                }
                                else
                                {
                                    ischeck= false;
                                }
                            }
                            else
                            {
                                ischeck = false;
                            }
                           // return 1;
                        }
                        else
                        {
                            ischeck = false;
                        }
                    }
                    else
                    {
                        ischeck = false;
                    }
                }
                else
                {
                    ischeck = false;
                }
            }
            catch (Exception ex)
            {
                log.Error("check_identifier_async Exception :" + ex.Message);

                ischeck = false;
            }
            //return Ok(ischeck);
            return ischeck;
        }


        [HttpGet("resend")]
        public bool resend(string key_code)
        {
            bool ischeck = false;
            try
            {

                log.Info("直接識別處理 個人識別代碼 : " + key_code);

                //call api 
                string clientIpAddress = _configuration["ConnIP:IP"]; //GetClientIpAddress(HttpContext);

                check_keynum keymodel = new check_keynum
                {
                    identifier = key_code
                    //identifier = "L2D0K"
                };
                //HashKeyModel keymodel = new HashKeyModel
                //{
                //    aes_col = "Education",
                //    mac_col = "Name,Zipcode",
                //    hash_table_name = "test_7",
                //    enc_key = "9787799D461C5CFE166AF12E25C5A7371B14631A2CA93AB03C9EB0D5710775B2",
                //    sep = ","
                //};

                string strkeymodel = JsonHelper.SerializeObject(keymodel);
                log.Info("resend_async Json   String " + strkeymodel);

                var apirestult = HttpHelper.PostUrl("resend_async ", strkeymodel);



                //var apirestult = HttpHelper.PostUrl(enc_api_func, strkeymodel);
                log.Info("resend_async Json  Return String " + apirestult);
                if (apirestult != "")
                {
                    JObject apidecode = JObject.Parse(apirestult);
                    string apistatus = apidecode["status"].ToString();
                    if (apistatus != "")
                    {
                        if (apistatus == "1")
                        {
                            string check = apidecode["check"].ToString();
                            if (check != "")
                            {
                                if (check == "yes")
                                {
                                    log.Info("resend_async Json   return true");

                                    ischeck = true;
                                }
                                else
                                {
                                    ischeck = false;
                                }
                            }
                            else
                            {
                                ischeck = false;
                            }
                            // return 1;
                        }
                        else
                        {
                            ischeck = false;
                        }
                    }
                    else
                    {
                        ischeck = false;
                    }
                }
                else
                {
                    ischeck = false;
                }
            }
            catch (Exception ex)
            {
                log.Error("resend_async Exception :" + ex.Message);

                ischeck = false;
            }
            //return Ok(ischeck);
            return ischeck;
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



    
        class ApiBody
        {
            public string doDeptno;
            public string type;
            public string doSno;
        }

    }
}