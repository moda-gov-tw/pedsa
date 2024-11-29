using log4net;
using Microsoft.Extensions.Configuration;
using Newtonsoft.Json;
using System;
using System.IO;
using System.Net.Http;
using System.Text;
using System.Threading.Tasks;

namespace DeIdWeb.Infrastructure.Service
{
    public class DpConnHelper
    {
        private readonly IHttpClientFactory _clientFactory;
        public static IConfiguration Configuration { get; set; }
        public DpConnHelper(IHttpClientFactory clientFactory)
        {
            var builder = new ConfigurationBuilder()
         .SetBasePath(Directory.GetCurrentDirectory())
         .AddJsonFile("appsettings.json");
            Configuration = builder.Build();
            _clientFactory = clientFactory;
        }

        public string returndownload()
        {
            string url = Configuration["Dp_API:URL"];
            return url + "web/";
        }

        public async Task<string> postasync(string apiname, object apiBody)
        {
            
            ILog log = LogManager.GetLogger(Startup.repository.Name, typeof(DpConnHelper));
            try
            {
                string url = Configuration["Dp_API:URL"];
                log.Info("web api url :" + url + "/" + apiname);
                var apiUrl = url+apiname;
                var jsstr = JsonConvert.SerializeObject(apiBody);
                log.Info("web api json :" + jsstr);

                var content = new StringContent(Newtonsoft.Json.JsonConvert.SerializeObject(apiBody), Encoding.UTF8, "application/json");

                using (var httpClient = _clientFactory.CreateClient())
                {
                    var response = await httpClient.PostAsync(apiUrl, content);

                    if (response.IsSuccessStatusCode)
                    {
                        // 處理成功響應
                        var responseContent = await response.Content.ReadAsStringAsync();
                        // 根據需要處理響應內容，這裡可以返回相應的值
                        return responseContent;
                    }
                    else
                    {
                        // 處理錯誤響應
                        return "error";
                    }
                }
            }
            catch (Exception ex)
            {
                // 處理異常
                return "error";
            }
        }


        public async Task<string> getasync(string apiname)
        {

            ILog log = LogManager.GetLogger(Startup.repository.Name, typeof(DpConnHelper));
            try
            {
                string url = Configuration["Dp_API:URL"];
                log.Info("web api url :" + url +  apiname);
                var apiUrl = url + apiname;
                //var jsstr = JsonConvert.SerializeObject(apiBody);
                //log.Info("web api json :" + jsstr);

                // 將 JSON 字串轉換為 URL 安全格式
               // var escapedJson = Uri.EscapeDataString(jsstr);

                // 使用 UriBuilder 來構建 URL
                var uriBuilder = new UriBuilder(apiUrl);
                // 在 query string 中添加參數
                var query = System.Web.HttpUtility.ParseQueryString(uriBuilder.Query);
               
                //query["jsstr"] = escapedJson; // 將轉換後的 JSON 字串添加到 query string
                uriBuilder.Query = query.ToString();

                using (var httpClient = _clientFactory.CreateClient())
                {
                    var response = await httpClient.GetAsync(apiUrl);

                    if (response.IsSuccessStatusCode)
                    {
                        // 處理成功響應
                        var responseContent = await response.Content.ReadAsStringAsync();
                        // 根據需要處理響應內容，這裡可以返回相應的值
                        return responseContent;
                    }
                    else
                    {
                        // 處理錯誤響應
                        return "error";
                    }
                }
            }
            catch (Exception ex)
            {
                // 處理異常
                return "error";
            }
        }


        public async Task<string> putasync(string apiname, object apiBody)
        {

            ILog log = LogManager.GetLogger(Startup.repository.Name, typeof(DpConnHelper));
            try
            {
                string url = Configuration["Dp_API:URL"];
                log.Info("web api url :" + url + apiname);
                var apiUrl = url + apiname;
                var jsstr = JsonConvert.SerializeObject(apiBody);
                log.Info("web api json :" + jsstr);

                var content = new StringContent(jsstr, Encoding.UTF8, "application/json");

                using (var httpClient = _clientFactory.CreateClient())
                {
                    var response = await httpClient.PutAsync(apiUrl, content);

                    if (response.IsSuccessStatusCode)
                    {
                        // 處理成功響應
                        var responseContent = await response.Content.ReadAsStringAsync();
                        // 根據需要處理響應內容，這裡可以返回相應的值
                        return responseContent;
                    }
                    else
                    {
                        // 處理錯誤響應
                        return "error";
                    }
                }
            
            }
            catch (Exception ex)
            {
                // 處理異常
                return "error";
            }
        }
    }
}
