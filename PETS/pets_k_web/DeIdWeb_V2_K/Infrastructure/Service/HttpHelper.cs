using log4net;
using Microsoft.Extensions.Configuration;
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Net;
using System.Net.Http;
using System.Text;
using System.Threading.Tasks;

namespace DeIdWeb_V2_K.Infrastructure.Service
{
    public class HttpHelper
    {
        public static IConfiguration Configuration { get; set; }

        public HttpHelper()
        {
            var builder = new ConfigurationBuilder()
            .SetBasePath(Directory.GetCurrentDirectory())
            .AddJsonFile("appsettings.json");
            Configuration = builder.Build();
        }
        public static string PostUrl(string apiname, string postData)
        {
            //http://140.96.178.114:5088
            ILog log = LogManager.GetLogger(Startup.repository.Name, typeof(HttpHelper));

            string result = "";
            try
            {
                string url = Configuration["DeIdWebAPI:URL"];
                log.Info("web api url :" + url + "/" + apiname);
                System.Net.ServicePointManager.ServerCertificateValidationCallback = (obj, X509certificate, chain, errors) => true;
                HttpWebRequest req = (HttpWebRequest)WebRequest.Create(url + "/" + apiname);

                req.Method = "POST";

                req.ContentType = "application/json";

                //req.Timeout = 300000;//请求超时时间

                req.ReadWriteTimeout = 3600000;

                byte[] data = Encoding.UTF8.GetBytes(postData);

                req.ContentLength = data.Length;

                using (Stream reqStream = req.GetRequestStream())
                {
                    reqStream.Write(data, 0, data.Length);

                    reqStream.Close();
                }

                HttpWebResponse resp = (HttpWebResponse)req.GetResponse();

                Stream stream = resp.GetResponseStream();

                //获取响应内容
                using (StreamReader reader = new StreamReader(stream, Encoding.UTF8))
                {
                    result = reader.ReadToEnd();
                }
            }
            catch (Exception e)
            {
                string ex = e.ToString();
                log.Error("PostUrl :" + e.Message.ToString());
            }
            log.Info("PostUrl result :" + result);

            return result;
        }


        public async Task<string> PostUrl_async(string apiname, string postData)
        {
            //http://140.96.178.114:5088
            ILog log = LogManager.GetLogger(Startup.repository.Name, typeof(HttpHelper));

            string result = "";
            try
            {
                string url = Configuration["DeIdWebAPI:URL"];
                log.Info("web api url :" + url + "/" + apiname);
               System.Net.ServicePointManager.ServerCertificateValidationCallback = (obj, X509certificate, chain, errors) => true;
                using (HttpClient client = new HttpClient())
                {
                    // 设置忽略 SSL 证书验证（仅供测试，生产环境请不要这样设置）
                    ServicePointManager.ServerCertificateValidationCallback = (obj, X509certificate, chain, errors) => true;

                    // 构建请求的 URL
                    string requestUrl = $"{url}/{apiname}";

                    // 构建请求的内容
                    HttpContent content = new StringContent(postData, Encoding.UTF8, "application/json");

                    // 发送异步 POST 请求
                    HttpResponseMessage response = await client.PostAsync(requestUrl, content);

                    // 确保请求成功
                    response.EnsureSuccessStatusCode();

                    // 获取响应内容
                    result = await response.Content.ReadAsStringAsync();
                }
            }
            catch (Exception e)
            {
                string ex = e.ToString();
                log.Error($"PostUrlAsync: {e.Message}");
                

                // 输出或记录详细的异常信息
                log.Error($"SSL Exception Details: {e.InnerException?.ToString()}");
            }

            log.Info($"PostUrlAsync result: {result}");

            return result;
        }

    }
}
