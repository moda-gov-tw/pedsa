using log4net;
using Microsoft.Extensions.Configuration;
using MySql.Data.MySqlClient;
using System;
using DeIdWeb_V2_K.Models;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using Dapper;

namespace DeIdWeb_V2_K.Infrastructure.Service
{
    public class SystemLog_Service
    {
        public static IConfiguration Configuration { get; set; }
        private ILog log = LogManager.GetLogger(Startup.repository.Name, typeof(SystemLog_Service));

        public SystemLog_Service()
        {
            var builder = new ConfigurationBuilder()
            .SetBasePath(Directory.GetCurrentDirectory())
            .AddJsonFile("appsettings.json");
            Configuration = builder.Build();
        }

        public List<SystemLogModel> GetSystemLogList(string wherestring)
        {
            Encoding.RegisterProvider(CodePagesEncodingProvider.Instance);
            string Connection = Configuration["ConnectionStrings:DefaultConnection"];
            List<SystemLogModel> lstmember = null;
            try
            {
                using (MySqlConnection conn = new MySqlConnection(Connection))
                {
                    string sql = "select ts.Id,member_id,logtime,logtype,case when logtype = '0' then 'Info' else 'Error' end as logtype_name,logcontent,tm.username from T_SystemLog as ts inner join T_Member as tm on ts.member_id = tm.Id order by logtime desc, logtype ";


                    lstmember = conn.Query<SystemLogModel>(sql).ToList();
                }

            }
            catch (Exception ex)
            {
                log.Error("Select GetSystemLogList Exception :" + ex.Message);
                //  return false;
                return lstmember;
            }
            return lstmember;
        }





        public bool InsertSystemLog(string member_id, string logtype, string logstep, string logcontent)
        {
            Encoding.RegisterProvider(CodePagesEncodingProvider.Instance);
            string Connection = Configuration["ConnectionStrings:DefaultConnection"];
            try
            {
                using (MySqlConnection conn = new MySqlConnection(Connection))
                {
                    string sql = "INSERT INTO T_SystemLog (Id,member_id,logtime,logtype,logstep,logcontent)VALUES(UUID(),@member_id,now(),@logtype,'@logstep',@logcontent ); ";
                    var datas = new SystemLogModel { member_id = int.Parse(member_id), logtype = int.Parse(logtype), logstep = logstep, logcontent = logcontent };
                    conn.Execute(sql, datas);
                }
                return true;
            }
            catch (Exception ex)
            {
                log.Error("InsertSystemLog Exception :" + ex.Message);
                return false;
            }

        }

    }
}
