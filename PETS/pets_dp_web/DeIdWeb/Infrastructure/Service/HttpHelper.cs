using log4net;
using Microsoft.Extensions.Configuration;
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Net;
using System.Text;
using System.Threading.Tasks;

namespace DeIdWeb.Infrastructure.Service
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
                log.Info("web api url :"+url+"/"+apiname);
                HttpWebRequest req = (HttpWebRequest)WebRequest.Create(url + "/" + apiname);

                req.Method = "POST";

                req.ContentType = "application/json";

                // req.Timeout = 20000;//请求超时时间

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
                log.Error("PostUrl :"+e.Message.ToString());
            }
            log.Info("PostUrl result :" + result);

            return result;
        }

    }
}
