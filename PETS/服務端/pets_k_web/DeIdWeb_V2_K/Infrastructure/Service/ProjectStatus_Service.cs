using Dapper;
using DeIdWeb_V2_K.Models;
using log4net;
using Microsoft.Extensions.Configuration;
using MySql.Data.MySqlClient;
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace DeIdWeb_V2_K.Infrastructure.Service
{
    public class ProjectStatus_Service
    {
        public static IConfiguration Configuration { get; set; }
        private ILog log = LogManager.GetLogger(Startup.repository.Name, typeof(ProjectStatus_Service));

        public ProjectStatus_Service()
        {
            var builder = new ConfigurationBuilder()
            .SetBasePath(Directory.GetCurrentDirectory())
            .AddJsonFile("appsettings.json");
            Configuration = builder.Build();
        }

        //public string selectProjectSparkStatus(int pid)
        //{

        //}

        public List<ProjectStatus> SelectProjectStatuis(int project_id)
        {
            List<ProjectStatus> lstPs = null;
            Encoding.RegisterProvider(CodePagesEncodingProvider.Instance);
            string Connection = Configuration["ConnectionStrings:DefaultConnection"];
            try
            {
                using (MySqlConnection conn = new MySqlConnection(Connection))
                {
                    string sql = "select project_id,project_status,statusname from T_ProjectStatus where project_id=@project_id";
                    var datas = new ProjectStatus { project_id = project_id};
                    lstPs = conn.Query<ProjectStatus>(sql, datas).ToList();
                }
                return lstPs;
            }
            catch (Exception ex)
            {
                log.Info("SelectProjectStatuis :"+ex.Message);
                return lstPs;
            }
        }
        public Boolean InsertProjectStauts(int project_id, int project_status, string statusname)
        {

            try
            {
                Encoding.RegisterProvider(CodePagesEncodingProvider.Instance);
                string Connection = Configuration["ConnectionStrings:DefaultConnection"];
                // string Connection = Configuration["ConnectionStrings:DefaultConnection"];
                using (MySqlConnection conn = new MySqlConnection(Connection))
                {
                    log.Info("statusname= " + statusname);
                    string s = statusname;
                    string utf8_string = Encoding.UTF8.GetString(Encoding.Default.GetBytes(s));

                    string sql = "insert into T_ProjectStatus(project_id,project_status,statusname,createtime)value(@project_id,@project_status,@statusname,now())";
                    log.Info("Insert ProjectStatus :"+sql);
                    var datas = new ProjectStatus { project_id = project_id, project_status = project_status, statusname = utf8_string };
                    conn.Execute(sql, datas);
                }
                return true;
            }
            catch (Exception ex)
            {
                log.Error("Insert ProjectStatus Exception :" + ex.Message.ToString());
                return false;
            }

        }

        public Boolean UpdateProjectSparkStauts(int pspark_id, string app_id,string stepstatus)
        {
            Encoding.RegisterProvider(CodePagesEncodingProvider.Instance);
            string Connection = Configuration["ConnectionStrings:DefaultConnection"];
            try
            {
                using (MySqlConnection conn = new MySqlConnection(Connection))
                {
                    string sql = "Update T_Project_SparkStatus_Management set stepstatus=@stepstatus,updatetime=now() where pspark_id=@pspark_id and app_id=@app_id";
                    var datas = new ProjectSparkMan {pspark_id=pspark_id,app_id=app_id,stepstatus=int.Parse(stepstatus) };
                    conn.Execute(sql, datas);
                }
                return true;
            }
            catch (Exception ex)
            {
                log.Error("UpdateProjectSparkStauts Exception :"+ex.Message);
                return false;
            }

        }

    }
}
