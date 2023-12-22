using Dapper;
using DeIdWeb.Models;
using log4net;
using Microsoft.Extensions.Configuration;
using MySql.Data.MySqlClient;
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;

namespace DeIdWeb.Infrastructure.Service
{
    public class Dept_Service
    {
        public static IConfiguration Configuration { get; set; }
        private ILog log = LogManager.GetLogger(Startup.repository.Name, typeof(Dept_Service));

        public Dept_Service()
        {
            var builder = new ConfigurationBuilder()
            .SetBasePath(Directory.GetCurrentDirectory())
            .AddJsonFile("appsettings.json");
            Configuration = builder.Build();
        }

        public List<Dept> GetDeptList(string wherestring)
        {
            Encoding.RegisterProvider(CodePagesEncodingProvider.Instance);
            string Connection = Configuration["ConnectionStrings:DefaultConnection"];
            List<Dept> lstDept = null;
            try
            {
                using (MySqlConnection conn = new MySqlConnection(Connection))
                {
                    string sql = "select Id,dept_name,createtime,case when updatetime is null then null else updatetime end as updatetime from T_Dept ";
                    if (wherestring != "")
                        sql = sql + " where dept_name=@dept_name";
                    var datas = new Dept { dept_name = wherestring };
                    lstDept = conn.Query<Dept>(sql, datas).ToList();
                }

            }
            catch (Exception ex)
            {
                log.Error("Select Dept Exception :" + ex.Message);
                //  return false;
                return lstDept;
            }
            return lstDept;
        } 
    }
}
