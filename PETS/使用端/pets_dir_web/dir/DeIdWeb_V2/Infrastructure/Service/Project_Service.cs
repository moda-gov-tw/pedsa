using Dapper;
using DeIdWeb_V2;
using DeIdWeb_V2.Models;
using log4net;
using Microsoft.Extensions.Configuration;
using MySql.Data.MySqlClient;
using PETs_Dir.Models;
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
namespace PETs_Dir.Infrastructure.Service
{
    public class Project_Service
    {
        public static IConfiguration Configuration { get; set; }
        private ILog log = LogManager.GetLogger(Startup.repository.Name, typeof(Project_Service));


        public Project_Service()
        {
            var builder = new ConfigurationBuilder()
            .SetBasePath(Directory.GetCurrentDirectory())
            .AddJsonFile("appsettings.json");
            Configuration = builder.Build();
        }

        public List<ProjectStatusModel> getserveripuploadfile(string service_ip)
        {
            List<ProjectStatusModel> lstPs = null;
            Encoding.RegisterProvider(CodePagesEncodingProvider.Instance);
            string Connection = Configuration["ConnectionStrings:DefaultConnection"];
            try
            {
                using (MySqlConnection conn = new MySqlConnection(Connection))
                {
                    string sql = "select project_id,service_ip,dataset_name from T_ProjectStatus where project_id=99999 and statusname='直接識別Hash完成'  and service_ip=@service_ip and createtime >= NOW() - INTERVAL 1 MINUTE;";
                    var datas = new ProjectStatusModel { service_ip = service_ip };
                    lstPs = conn.Query<ProjectStatusModel>(sql, datas).ToList();
                }
                return lstPs;
            }
            catch (Exception ex)
            {
                log.Info("SelectProjectStatuis :" + ex.Message);
                return lstPs;
            }
        }


        public List<ProjectStatusModel> getserveripuploadfilelist()
        {
            List<ProjectStatusModel> lstPs = null;
            Encoding.RegisterProvider(CodePagesEncodingProvider.Instance);
            string serviceip = Configuration["ConnIP:IP"];

            string Connection = Configuration["ConnectionStrings:DefaultConnection"];
            try
            {
                using (MySqlConnection conn = new MySqlConnection(Connection))
                {
                    string sql = "select ps_id,key_code,project_id,service_ip,dataset_name,project_status,statusname,createtime,updatetime from T_ProjectStatus where project_id=99999  and service_ip=@service_ip  order by createtime desc;";
                    var datas = new ProjectStatusModel { service_ip = serviceip };
                    lstPs = conn.Query<ProjectStatusModel>(sql, datas).ToList();
                }
                return lstPs;
            }
            catch (Exception ex)
            {
                log.Info("SelectProjectStatuis :" + ex.Message);
                return lstPs;
            }
        }
    }
}
