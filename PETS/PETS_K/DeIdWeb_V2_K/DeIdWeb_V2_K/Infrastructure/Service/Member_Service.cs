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

namespace DeIdWeb_V2_K.Infrastructure.Service
{

    public class Member_Service
    {
        public static IConfiguration Configuration { get; set; }
        private ILog log = LogManager.GetLogger(Startup.repository.Name, typeof(Member_Service));

        public Member_Service()
        {
            var builder = new ConfigurationBuilder()
            .SetBasePath(Directory.GetCurrentDirectory())
            .AddJsonFile("appsettings.json");
            Configuration = builder.Build();
        }

        public List<Member> GetMemberList(string wherestring)
        {
            Encoding.RegisterProvider(CodePagesEncodingProvider.Instance);
            string Connection = Configuration["ConnectionStrings:DefaultConnection"];
            List<Member> lstmember = null;
            try
            {
                using (MySqlConnection conn = new MySqlConnection(Connection))
                {
                    string sql = "select T_Member.id,useraccount,dept_name,isAdmin,case when isAdmin=0 then '否' else '是' end as isAdminNM,T_Member.createtime from T_Member inner join T_Dept on T_Member.dept_id = T_Dept.Id  ";
                    if (wherestring != "")
                    sql = sql + " where useraccount=@UserAccount or username=@UserName or email=@Email ";
                    var datas = new Member { UserAccount=wherestring,UserName=wherestring,Email=wherestring};
                    lstmember = conn.Query<Member>(sql, datas).ToList();
                }

            }
            catch (Exception ex)
            {
                log.Error("Select Member Exception :" + ex.Message);
                //  return false;
                return lstmember;
            }
            return lstmember;
        }


        public bool UpdateUserPass(string pid, string userAcc, string newpass)
        {
            Encoding.RegisterProvider(CodePagesEncodingProvider.Instance);
            string Connection = Configuration["ConnectionStrings:DefaultConnection"];
            try
            {
                using (MySqlConnection conn = new MySqlConnection(Connection))
                {
                    string sql = "Update T_Member set password=@Password where id=@Id and useraccount=@UserAccount";
                    var datas = new Member { Id = int.Parse(pid), UserAccount = userAcc,Password=newpass};
                    conn.Execute(sql, datas);
                }
                return true;
            }
            catch (Exception ex)
            {
                log.Error("UpdateProjectSparkStauts Exception :" + ex.Message);
                return false;
            }

        }


        public List<Member> GetMember(string userAcc)
        {
            Encoding.RegisterProvider(CodePagesEncodingProvider.Instance);
            string Connection = Configuration["ConnectionStrings:DefaultConnection"];
            List<Member> lstmember = null;
            try
            {
                using (MySqlConnection conn = new MySqlConnection(Connection))
                {
                    string sql = "select * from T_Member";
                    if (userAcc != "")
                        sql = sql + " where useraccount=@UserAccount";
                    var datas = new Member { UserAccount = userAcc };
                    lstmember = conn.Query<Member>(sql, datas).ToList();
                }

            }
            catch (Exception ex)
            {
                log.Error("Select Member Exception :" + ex.Message);
                //  return false;
                return lstmember;
            }
            return lstmember;
        }
    }
}
