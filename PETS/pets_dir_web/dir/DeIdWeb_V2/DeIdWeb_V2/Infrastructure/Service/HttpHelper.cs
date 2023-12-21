using log4net;
using Microsoft.Extensions.Configuration;
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Net;
using System.Text;
using System.Threading.Tasks;



namespace DeIdWeb_V2.Infrastructure.Service
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
                string url_Group = Configuration["DeIdWebAPI:GroupSetting"];
                string new_url = "";
                if (url_Group == "0")
                {    
                    log.Info(" G0 web api url :" + url + "/" + apiname);
                }
                else
                {
                    log.Info("G1 web api url :" + url + "/" + apiname);
                }
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

        public static string PostGroupUrl(string apiname, string postData,string group_name)
        {
            //http://140.96.178.114:5088
            ILog log = LogManager.GetLogger(Startup.repository.Name, typeof(HttpHelper));

            string result = "";
            //string group_name=""; //for test gau
            try
            {
                string url = Configuration["DeIdWebAPI:URL"];
                string url_Group = Configuration["DeIdWebAPI:GroupSetting"];
                string new_url = "";
                //log.Info($"url_Group : {url_Group}");
                //log.Info($"apiname : {apiname}");
                //log.Info($"postData : {postData}");
                //log.Info($"group_name : {group_name}");
                if (url_Group == "0")
                {   // G0 web api url :https://nginx_compose:5088/H1/aesgroup_async
                    log.Info(" G0 web api url :" + url + "/" + apiname);
                    new_url = url + "/" + apiname;
                }
                else
                {
                    log.Info("G1 web api url :" + url + "/"+ group_name+"/" + apiname);
                    new_url = url + "/" + group_name+"/"+apiname;
                }
                

                //20230517, gau add for switch to H1 or H2 (hadoop cluster) string[] words = phrase.Split(' ');
                string switch_group_name=""; //s1.Contains
 /*                
                if(postData.Contains("jsonBase64")){
                    switch_group_name=group_name;
                }

                else{ //userId
                   //List<string> keymodel_list =
                   //            JsonConvert.DeserializeObject<List<string>>(postData);

                    string userId_str = JsonConvert.DeserializeObject<dynamic>(postData).userId;           

                    //string userId_str=keymodel_list["userId"].ToString();
                    switch_group_name="G"+userId_str ;   
                }
*/     
                switch_group_name=group_name;           
                log.Info(" ---- switch_group_name :" + switch_group_name);


                //gau, 20230517 add
                List<string> first_72_group_name_list = new List<string>();

                for (int i = 0; i <= 72; i++) { 
                    first_72_group_name_list.Add("G"+i.ToString());
                }
                string cluster_name="";
                if(first_72_group_name_list.Contains(switch_group_name)){

                    cluster_name="H1";

                }else{
                    cluster_name="H2";
                }


                

                if (url_Group == "0")
                {   // G0 web api url :https://nginx_compose:5088/H1/aesgroup_async
                    log.Info(" G0 web api url :" + url + "/" + apiname);
                    new_url = url + "/" + apiname;
                }
                else
                {
                    log.Info("----------------H*--1 or 2------------  web api url :" + url + "/"+ cluster_name+"/" + apiname);
                    new_url = url + "/" + cluster_name+"/"+apiname;

                }
        //end, 20230517, gau add for switch to H1 or H2 (hadoop cluster) string[] words = phrase.Split(' ');


                
                System.Net.ServicePointManager.ServerCertificateValidationCallback = (obj, X509certificate, chain, errors) => true;
                HttpWebRequest req = (HttpWebRequest)WebRequest.Create(new_url);
                log.Info("---1");
                req.Method = "POST";

                req.ContentType = "application/json";

                //req.Timeout = 300000;//请求超时时间

                req.ReadWriteTimeout = 3600000;

                byte[] data = Encoding.UTF8.GetBytes(postData);

                req.ContentLength = data.Length;
                log.Info("---2");
                using (Stream reqStream = req.GetRequestStream())
                {
                    reqStream.Write(data, 0, data.Length);

                    reqStream.Close();
                }
                log.Info("---3");
                HttpWebResponse resp = (HttpWebResponse)req.GetResponse();

                Stream stream = resp.GetResponseStream();
                log.Info("---4");
                //获取响应内容
                using (StreamReader reader = new StreamReader(stream, Encoding.UTF8))
                {
                    result = reader.ReadToEnd();
                }
                log.Info("---5");
            }
            catch (Exception e)
            {
                string ex = e.ToString();
                log.Error("PostUrl group :" + e.Message.ToString());
            }
            log.Info("PostUrl result group1 :" + result);

            return result;
        }

    }
}
