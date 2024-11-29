using Dapper;
using DeIdWeb_V2_K.Models;
using log4net;
using Microsoft.Extensions.Configuration;
using MySql.Data.MySqlClient;
using System;
using System.Collections.Generic;
using System.Data;
using System.IO;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace DeIdWeb_V2_K.Infrastructure.Service
{
    public class MySqlDBHelper
    {
        //  private IConfiguration _configuration;
        public static IConfiguration Configuration { get; set; }
        private ILog log = LogManager.GetLogger(Startup.repository.Name, typeof(MySqlDBHelper));

        public MySqlDBHelper()
        {
            var builder = new ConfigurationBuilder()
            .SetBasePath(Directory.GetCurrentDirectory())
            .AddJsonFile("appsettings.json");
            Configuration = builder.Build();
        }
        
        /// <summary>
        /// 利用MysqlDataReader曲线构造并填充DataTable
        /// </summary>
        /// <param name="connectionString"></param>
        /// <param name="sql"></param>
        /// <returns></returns>
        public static DataTable ExecuteDataTable(string connectionString, string sql)
        {
            DataTable dt = new DataTable();
            MySqlDataReader dr = MySqlHelper.ExecuteReader(connectionString, sql);


            try
            {
                int fieldCount = dr.FieldCount;


                //获取schema并填充第一行数据
                if (dr.Read())
                {
                    for (int i = 0; i < fieldCount; i++)
                    {
                        string colName = dr.GetName(i);
                        dt.Columns.Add(colName, dr[i].GetType());
                    }


                    DataRow newrow = dt.NewRow();
                    for (int i = 0; i < fieldCount; i++)
                    {
                        newrow[i] = dr[i];
                    }
                    dt.Rows.Add(newrow);
                }

                //填充后续数据
                while (dr.Read())
                {
                    DataRow newrow = dt.NewRow();
                    for (int i = 0; i < fieldCount; i++)
                    {
                        newrow[i] = dr[i];
                    }
                    dt.Rows.Add(newrow);
                }
                dt.AcceptChanges();
            }
            catch (Exception e1)
            {
                Console.WriteLine(e1.Message);
                //throw;
            }
            finally
            {
                dr.Close();
            }


            return dt;
        }

           public Boolean InsertDB(string sql)
        {
            log.Info("InsertDB InsertProjectDB :" +sql);

            Encoding.RegisterProvider(CodePagesEncodingProvider.Instance);
            string Connection = Configuration["ConnectionStrings:DefaultConnection"];
            try
            {
                MySqlConnection conn = new MySqlConnection(Connection);
                conn.Execute(sql);
                return true;
            }
            catch (Exception ex)
            {
                log.Error("InsertDB InsertProjectDB :"+ex.Message.ToString());
                return false;
            }

        }

        public Boolean InsertSparkStauts(List<ProjectSparkMan> objpsm)
        {
            Encoding.RegisterProvider(CodePagesEncodingProvider.Instance);
            string Connection = Configuration["ConnectionStrings:DefaultConnection"];
            try
            {
                using (MySqlConnection conn = new MySqlConnection(Connection))
                {
                    string sql = "insert into T_Project_SparkStatus_Management(app_id,celery_id,project_id,step,stepstatus,createtime)value(@app_id,@celery_id,@project_id,@step,@stepstatus,now())";
                    conn.Execute(sql, objpsm);
                }
                return true;
            }
            catch (Exception ex)
            {
                log.Error("InsertSparkStauts Exception :"+ex.Message);
                return false;
            }

        }
        public Boolean UpdateProjectJobStauts(int project_id, int project_status, string jobvalue,string job_tb,string jobrule)
        {
            Encoding.RegisterProvider(CodePagesEncodingProvider.Instance);
            string Connection = Configuration["ConnectionStrings:DefaultConnection"];
            try
            {
                using (MySqlConnection conn = new MySqlConnection(Connection))
                {
                    string sql = "Update T_ProjectJobStatus set jobname=@jobname,updatetime=now(),project_jobstatus=@project_jobstatus where project_id=@project_id and jobrule=@jobrule";
                    var datas = new ProjectJob { project_id = project_id, jobname = jobvalue,project_jobstatus=project_status,jobrule=jobrule};
                    conn.Execute(sql, datas);
                }
                return true;
            }
            catch (Exception ex)
            {
                log.Info("UpdateProjectJobStauts :" + ex.Message.ToString());
                return false;
            }

        }

        public Boolean InsertProjectJobStauts(List<ProjectJob> objpsm)
        {
            Encoding.RegisterProvider(CodePagesEncodingProvider.Instance);
            string Connection = Configuration["ConnectionStrings:DefaultConnection"];
            try
            {
                using (MySqlConnection conn = new MySqlConnection(Connection))
                {
                    string sql = "insert into T_ProjectJobStatus(project_id,project_jobstatus,jobname,job_tb,jobrule,createtime)value(@project_id,@project_jobstatus,@jobname,@job_tb,@jobrule,now())";
                    conn.Execute(sql, objpsm);
                }
                return true;
            }
            catch (Exception ex)
            {
                log.Error("InsertProjectJobStauts Exception :" + ex.Message);
                return false;
            }

        }


        public List<Member> SelectMemberAcc(string useracc)
        {
            List<Member> lstmember = null;

            try
            {
                Encoding.RegisterProvider(CodePagesEncodingProvider.Instance);
                string Connection = Configuration["ConnectionStrings:DefaultConnection"];

                using (MySqlConnection conn = new MySqlConnection(Connection))
                {
                    //var Results = db.Query<TableSqlDbType>(query, new { C1 = "10001" });
                    string strSql = "select * from T_Member where useraccount=@UserAccount ";

                    lstmember = conn.Query<Member>(strSql, new Member { UserAccount = useracc }).ToList();
                }
            }
            catch (Exception ex)
            {
                string exmsg = ex.Message;
                log.Error(" SelectMemberAcc :" + exmsg);

            }

            return lstmember;
        }



        public List<Dept> selectDept(string deptname)
        {
            List<Dept> deptlist = null;

            try
            {
                Encoding.RegisterProvider(CodePagesEncodingProvider.Instance);
                string Connection = Configuration["ConnectionStrings:DefaultConnection"];

                using (MySqlConnection conn = new MySqlConnection(Connection))
                {
                    //var Results = db.Query<TableSqlDbType>(query, new { C1 = "10001" });
                    string strSql = "select * from T_Dept where dept_name=@dept_name ";

                    deptlist = conn.Query<Dept>(strSql, new { dept_name = deptname }).ToList();
                }
            }
            catch (Exception ex)
            {
                string exmsg = ex.Message;
                log.Error(" selectDept :" + exmsg);

            }

            return deptlist;
        }

        public List<Dept> selectDept()
        {
            List<Dept> deptlist = null;

            try
            {
                Encoding.RegisterProvider(CodePagesEncodingProvider.Instance);
                string Connection = Configuration["ConnectionStrings:DefaultConnection"];

                using (MySqlConnection conn = new MySqlConnection(Connection))
                {
                    //var Results = db.Query<TableSqlDbType>(query, new { C1 = "10001" });
                    string strSql = "select * from T_Dept ";

                    deptlist = conn.Query<Dept>(strSql).ToList();
                }
            }
            catch (Exception ex)
            {
                string exmsg = ex.Message;
                log.Error(" selectDept :" + exmsg);

            }

            return deptlist;
        }



        public List<ProjectJob> SelectProjectJobStautsByJob(string pid, int jobstatus)
        {

            Encoding.RegisterProvider(CodePagesEncodingProvider.Instance);
            string Connection = Configuration["ConnectionStrings:DefaultConnection"];
            List<ProjectJob> lstproj = null;
            try
            {
                using (MySqlConnection conn = new MySqlConnection(Connection))
                {
                    string sql = "select * from T_ProjectJobStatus where project_id=@project_id and project_jobstatus=@project_jobstatus ";
                    var datas = new ProjectJob { project_id = int.Parse(pid), project_jobstatus = jobstatus };
                    lstproj = conn.Query<ProjectJob>(sql, datas).ToList();
                }

            }
            catch (Exception ex)
            {
                log.Error("InsertProjectJobStauts Exception :" + ex.Message);
                //  return false;
            }
            return lstproj;
        }

        public List<ProjectJob> SelectProjectJobStauts(string pid,int jobstatus,string projectjobname)
        {

            Encoding.RegisterProvider(CodePagesEncodingProvider.Instance);
            string Connection = Configuration["ConnectionStrings:DefaultConnection"];
            List<ProjectJob> lstproj = null;
            try
            {
                using (MySqlConnection conn = new MySqlConnection(Connection))
                {
                    string sql = "select * from T_ProjectJobStatus where project_id=@project_id and jobrule=@jobname and project_jobstatus=@project_jobstatus ";
                    var datas = new ProjectJob { project_id = int.Parse(pid),jobname= projectjobname,project_jobstatus=jobstatus };
                    lstproj = conn.Query<ProjectJob>(sql, datas).ToList();
                }
                
            }
            catch (Exception ex)
            {
                log.Error("InsertProjectJobStauts Exception :" + ex.Message);
             //  return false;
            }
            return lstproj;
        }
        public List<Member> SelectMember(string sql)
        {
            //DataTable dt = new DataTable();
            List<Member> memberlist = new List<Member>();
            
            Encoding.RegisterProvider(CodePagesEncodingProvider.Instance);
            string Connection = Configuration["ConnectionStrings:DefaultConnection"];
            try
            {
                MySqlConnection conn = new MySqlConnection(Connection);

                var list = conn.Query<Member>(sql);
                foreach (var item in list)
                {
                    Member ImemberInfo = new Member();
                    ImemberInfo.Id = item.Id;
                    ImemberInfo.UserAccount = item.UserAccount;
                    ImemberInfo.UserName = item.UserName;
                    ImemberInfo.Password = item.Password;
                    ImemberInfo.IsAdmin = item.IsAdmin;
                    ImemberInfo.Email = item.Email;
                    memberlist.Add(ImemberInfo);
                }
                return memberlist;
            }
            catch (Exception ex)
            {
                log.Error("SelectMember Exception :"+ex.Message);
                return memberlist;
            }

        }

        public List<Project> SelectProject(string sql)
        {
            //DataTable dt = new DataTable();
            List<Project> memberlist = new List<Project>();
            Member ImemberInfo = new Member();
            Encoding.RegisterProvider(CodePagesEncodingProvider.Instance);
            string Connection = Configuration["ConnectionStrings:DefaultConnection"];
            try
            {
                MySqlConnection conn = new MySqlConnection(Connection);

                var list = conn.Query<Project>(sql).ToList();
               
                return list;
            }
            catch (Exception ex)
            {
                log.Error("SelectProject Error :"+ex.Message.ToString());
                return null;
            }

        }

        public void UpdateR1R2(string r1, string r2)
        {
            Encoding.RegisterProvider(CodePagesEncodingProvider.Instance);
            string Connection = Configuration["ConnectionStrings:DefaultConnection"];
            try
            {
                MySqlConnection conn = new MySqlConnection(Connection);
                conn.Execute("update T_Project set r1_data = @r1_data, r2_data=@r2_data where ps_id = 5", new { r1_data = r1, r2_data = r2 });
            }
            catch (Exception ex)
            {
                log.Error("UpdateR1R2 Exception :"+ex.Message);
            }
        }

        public void CancelProjectDeleteData(int ps_id)
        {
            Encoding.RegisterProvider(CodePagesEncodingProvider.Instance);
            string Connection = Configuration["ConnectionStrings:DefaultConnection"];
            try
            {
                MySqlConnection conn = new MySqlConnection(Connection);
                string delstr = "Delete from T_Project_SparkStatus_Management where project_id=@project_id;" +
                    "Delete from T_utilityResult where project_id=@project_id;" +
                    "Delete from T_Project_RiskTable where project_id=@project_id;" +
                    "Delete from T_ProjectJobStatus where project_id=@project_id;" +
                    "Delete from T_Pro_DistinctTB where project_id=@project_id;" +
                    "Delete from T_Project_FinalTable where proj_id=@project_id;" +
                    "Update T_Project_SampleTable set  target_col='' where project_id=@project_id;"+
                "Delete from T_Project_NumStatValue where proj_id=@project_id";
                conn.Execute(delstr, new { project_id = ps_id });
            }
            catch (Exception ex)
            {
                log.Error("DeleteProject Exception :" + ex.Message);
            }
        }

        public void ResetML(int ps_id)
        {
            Encoding.RegisterProvider(CodePagesEncodingProvider.Instance);
            string Connection = Configuration["ConnectionStrings:DefaultConnection"];
            try
            {
                MySqlConnection conn = new MySqlConnection(Connection);
                string delstr =
                    "Delete from T_utilityResult where project_id=@project_id;" +
                    "Update T_ProjectStatus set project_status = 11 where project_id = @project_id;"+
                    "Update T_Project_SampleTable set  target_col='' where project_id=@project_id;";
                conn.Execute(delstr, new { project_id = ps_id });
            }
            catch (Exception ex)
            {
                log.Error("DeleteProject Exception :" + ex.Message);
            }
        }

        public void UpdateProjectStatus(int ps_id,int status)
        {
            Encoding.RegisterProvider(CodePagesEncodingProvider.Instance);
            string Connection = Configuration["ConnectionStrings:DefaultConnection"];
            try
            {
                MySqlConnection conn = new MySqlConnection(Connection);
                conn.Execute("update T_ProjectStatus set project_status = @pstatus where project_id = @project_id", new { project_id=ps_id, pstatus = status });
            }
            catch (Exception ex)
            {
                log.Error("UpdateProjectStatus Exception :" + ex.Message);
            }
        }

        public List<Project> CheckProjectStatus(string project_name)
        {
            List<Project> projectlst = null;
            Encoding.RegisterProvider(CodePagesEncodingProvider.Instance);
            string Connection = Configuration["ConnectionStrings:DefaultConnection"];
            try
            {
                MySqlConnection conn = new MySqlConnection(Connection);
                string sql= "select tp.project_id,tp.project_name,tp.project_cht,tps.project_status from T_Project as tp inner join T_ProjectStatus as tps on tp.project_id = tps.project_id where tp.project_name = @Project_name";
                var datas = new Project {project_name=project_name };
                projectlst = conn.Query<Project>(sql, datas).ToList();
            }
            catch (Exception ex)
            {
                log.Error("CheckProjectStatus Exception :" + ex.Message);
            }
            return projectlst;
        }

        public void DeleteProject (int ps_id)
        {
            Encoding.RegisterProvider(CodePagesEncodingProvider.Instance);
            string Connection = Configuration["ConnectionStrings:DefaultConnection"];
            try
            {
                MySqlConnection conn = new MySqlConnection(Connection);
                string delstr = "Delete from T_Project_SparkStatus_Management where project_id=@project_id;" +
                    "Delete from T_Project_SampleTable where project_id=@project_id;" +
                    "Delete from T_ProjectStatus where project_id=@project_id;" +
                    "Delete from T_ProjectSampleData where project_id=@project_id;" +
                    "Delete from T_ProjectJobStatus where project_id=@project_id;" +
                    "Delete from T_Project where project_id=@project_id;" +
                    "Delete from T_Pro_DistinctTB where project_id=@project_id;" +
                    "Delete from T_Project_FinalTable where proj_id=@project_id;" +
                    "Delete from T_Project_NumStatValue where proj_id=@project_id";
                conn.Execute(delstr, new { project_id = ps_id });
            }
            catch (Exception ex)
            {
                log.Error("DeleteProject Exception :" + ex.Message);
            }
        }


        public void DeleteDept(int dept_id)
        {
            Encoding.RegisterProvider(CodePagesEncodingProvider.Instance);
            string Connection = Configuration["ConnectionStrings:DefaultConnection"];
            try
            {
                MySqlConnection conn = new MySqlConnection(Connection);
                string delstr = "Delete from T_Dept where Id=@Id;";
                conn.Execute(delstr, new Dept { Id = dept_id });
            }
            catch (Exception ex)
            {
                log.Error("DeleteDept Exception :" + ex.Message);
            }
        }

        public List<Member> selectdeptbymember(int dept_id)
        {
            List<Member> lstmember = null;
            Encoding.RegisterProvider(CodePagesEncodingProvider.Instance);
            string Connection = Configuration["ConnectionStrings:DefaultConnection"];
            try
            {
                MySqlConnection conn = new MySqlConnection(Connection);
                string delstr = "select useraccount from T_Member where dept_id=@dept_id;";
                var datas=new Member { dept_id = dept_id };
                lstmember = conn.Query<Member>(delstr, datas).ToList();

            }
            catch (Exception ex)
            {
                log.Error("DeleteDept Exception :" + ex.Message);
            }

            return lstmember;
        }

        public bool InsertDept(string deptname)
        {

            try
            {
                Encoding.RegisterProvider(CodePagesEncodingProvider.Instance);
                string Connection = Configuration["ConnectionStrings:DefaultConnection"];
                log.Info("mysql connection :" + Connection);
                // string Connection = Configuration["ConnectionStrings:DefaultConnection"];
                using (MySqlConnection conn = new MySqlConnection(Connection))
                {
                    string sql = "insert into T_Dept(dept_name,createtime)value(@dept_name,now())";
                    var datas = new Dept { dept_name = deptname };
                    conn.Execute(sql, datas);
                }
                return true;
            }
            catch (Exception ex)
            {
                log.Error("InsertDept :" + ex.Message.ToString());
                return false;
            }

        }


        public void DeleteUser(int user_id)
        {
            Encoding.RegisterProvider(CodePagesEncodingProvider.Instance);
            string Connection = Configuration["ConnectionStrings:DefaultConnection"];
            try
            {
                MySqlConnection conn = new MySqlConnection(Connection);
                string delstr = "Delete from T_Member where Id=@Id;";
                conn.Execute(delstr, new Member { Id = user_id });
            }
            catch (Exception ex)
            {
                log.Error("DeleteUser Exception :" + ex.Message);
            }
        }


        //public void CancelProjectDeleteData(int ps_id)
        //{
        //    Encoding.RegisterProvider(CodePagesEncodingProvider.Instance);
        //    string Connection = Configuration["ConnectionStrings:DefaultConnection"];
        //    try
        //    {
        //        MySqlConnection conn = new MySqlConnection(Connection);
        //        string delstr = "Delete from T_Project_SparkStatus_Management where project_id=@project_id;" +



        //            "Delete from T_ProjectJobStatus where project_id=@project_id;" +

        //            "Delete from T_Pro_DistinctTB where project_id=@project_id;" +
        //            "Delete from T_Project_FinalTable where proj_id=@project_id;" +
        //            "Delete from T_Project_NumStatValue where proj_id=@project_id";
        //        conn.Execute(delstr, new { project_id = ps_id });
        //    }
        //    catch (Exception ex)
        //    {
        //        log.Error("DeleteProject Exception :" + ex.Message);
        //    }
        //}



        public Boolean InsertProjectStauts(int project_id, int project_status, string statusname)
        {

            try
            {
                Encoding.RegisterProvider(CodePagesEncodingProvider.Instance);
                string Connection = Configuration["ConnectionStrings:DefaultConnection"];
                log.Info("mysql connection :" + Connection);
                // string Connection = Configuration["ConnectionStrings:DefaultConnection"];
                using (MySqlConnection conn = new MySqlConnection(Connection))
                {
                    string sql = "insert into T_ProjectStatus(project_id,project_status,statusname,createtime)value(@project_id,@project_status,@statusname,now())";
                    var datas = new ProjectStatus { project_id = project_id, project_status = project_status, statusname = statusname };
                    conn.Execute(sql, datas);
                }
                return true;
            }
            catch (Exception ex)
            {
                log.Error("Insert ProjectStatus :"+ex.Message.ToString());
                return false;
            }

        }

        public Boolean UpdateProjectStauts(int project_id, int project_status, string statusname)
        {
            Encoding.RegisterProvider(CodePagesEncodingProvider.Instance);
            string Connection = Configuration["ConnectionStrings:DefaultConnection"];
            try
            {
                using (MySqlConnection conn = new MySqlConnection(Connection))
                {
                    string sql = "Update T_ProjectStatus set project_status=@project_status,statusname=@statusname,updatetime=now() where project_id=@project_id";
                    var datas = new ProjectStatus { project_id = project_id, project_status = project_status, statusname = statusname };
                    conn.Execute(sql, datas);
                }
                return true;
            }
            catch (Exception ex)
            {
                log.Info("UpdateProjectStauts :"+ex.Message.ToString());
                return false;
            }

        }

        public List<UtilityResult> SelectProUtilityResultCount(int pid)
        {
            List<UtilityResult> lstdistcount = null;
            try
            {
                Encoding.RegisterProvider(CodePagesEncodingProvider.Instance);
                string Connection = Configuration["ConnectionStrings:DefaultConnection"];

                using (MySqlConnection conn = new MySqlConnection(Connection))
                {
                    //pid = 123;
                    //var Results = db.Query<TableSqlDbType>(query, new { C1 = "10001" });
                    string strSql = "select distinct project_id,deIdTbl,target_col from T_utilityResult where project_id=@project_id ";
                    var datas = new UtilityResult { project_id = pid };
                    lstdistcount = conn.Query<UtilityResult>(strSql, datas).ToList();
                }
            }
            catch (Exception ex)
            {
                string exmsg = ex.Message;
                log.Error("SelectProUtilityResultCount Exception :" + exmsg);

            }
            return lstdistcount;
        }

        public List<RiskDataModel> SelectProjRiskTable(int pid, string pro_tb)
        {
            List<RiskDataModel> lstdistcount = null;
            try
            {
                Encoding.RegisterProvider(CodePagesEncodingProvider.Instance);
                string Connection = Configuration["ConnectionStrings:DefaultConnection"];

                using (MySqlConnection conn = new MySqlConnection(Connection))
                {
                    //pid = 123;
                    //var Results = db.Query<TableSqlDbType>(query, new { C1 = "10001" });
                    string strSql = "select project_name,dbname,tblname,r1,r2,r3,r4,r5,rs1,rs2,rs3,rs4,rs5 from T_Project_RiskTable where project_id=@project_id and tblname=@tblname ";
                    var datas = new RiskDataModel { project_id = pid ,tblname=pro_tb};
                    lstdistcount = conn.Query<RiskDataModel>(strSql, datas).ToList();
                }
            }
            catch (Exception ex)
            {
                string exmsg = ex.Message;
                log.Error("RiskDataModel Exception :" + exmsg);

            }
            return lstdistcount;
        }
        public List<UtilityResult> SelectdisResultModelCount(int pid, string target_col,string deIdTbl)
        {
            List<UtilityResult> lstdistcount = null;
            try
            {
                Encoding.RegisterProvider(CodePagesEncodingProvider.Instance);
                string Connection = Configuration["ConnectionStrings:DefaultConnection"];

                using (MySqlConnection conn = new MySqlConnection(Connection))
                {
                    //var Results = db.Query<TableSqlDbType>(query, new { C1 = "10001" });
                    string strSql = "select  deIdTbl,target_col,model from T_utilityResult where project_id=@project_id and deIdTbl=@deIdTbl and target_col=@target_col order by model ";
                    var datas = new UtilityResult { project_id = pid, target_col = target_col ,deIdTbl=deIdTbl};
                    lstdistcount = conn.Query<UtilityResult>(strSql, datas).ToList();
                }
            }
            catch (Exception ex)
            {
                string exmsg = ex.Message;
                log.Error("SelectProUtilityResultCount Exception :" + exmsg);

            }
            return lstdistcount;
        }


        public List<UtilityResult> SelectProUtilityResult(int pid, string target_col, string model)
        {
            List<UtilityResult> lstdistcount = null;
            try
            {
                Encoding.RegisterProvider(CodePagesEncodingProvider.Instance);
                string Connection = Configuration["ConnectionStrings:DefaultConnection"];

                using (MySqlConnection conn = new MySqlConnection(Connection))
                {
                    //var Results = db.Query<TableSqlDbType>(query, new { C1 = "10001" });
                    string strSql = "select target_col,model,MLresult from T_utilityResult where project_id=@project_id and target_col=@target_col and model=@model";
                    var datas = new UtilityResult { project_id = pid, target_col = target_col, model = model };
                    lstdistcount = conn.Query<UtilityResult>(strSql, datas).ToList();
                }
            }
            catch (Exception ex)
            {
                string exmsg = ex.Message;
                log.Error("SelectProUtilityResultCount Exception :" + exmsg);

            }
            return lstdistcount;
        }


        public List<ProjectSparkMan> SelectProjectJobStatusByProject(string project_id,string step)
        {
            List<ProjectSparkMan> lstProjectSparkJob = null;
            try
            {
                Encoding.RegisterProvider(CodePagesEncodingProvider.Instance);
                string Connection = Configuration["ConnectionStrings:DefaultConnection"];

                using (MySqlConnection conn = new MySqlConnection(Connection))
                {
                    //var Results = db.Query<TableSqlDbType>(query, new { C1 = "10001" });
                    string strSql = "select app_id,celery_id,project_id,step,stepstatus from T_Project_SparkStatus_Management where project_id=@project_id and step=@step and stepstatus <100 ";
                    
                    lstProjectSparkJob = conn.Query<ProjectSparkMan>(strSql, new { project_id = project_id,step=step }).ToList();
                }
            }
            catch (Exception ex)
            {
                string exmsg = ex.Message;
                log.Error(" SelectProjectJobStatusByProject :"+exmsg);

            }
            return lstProjectSparkJob;
        }

        public List<AppStatusModel> SelectProjectAppStatus()
        {
            List<AppStatusModel> lstProjectSparkJob = null;
            try
            {
                Encoding.RegisterProvider(CodePagesEncodingProvider.Instance);
                string Connection = Configuration["ConnectionStrings:DefaultConnection"];

                using (MySqlConnection conn = new MySqlConnection(Connection))
                {
                    //var Results = db.Query<TableSqlDbType>(query, new { C1 = "10001" });
                    string strSql = "SELECT id,Application_Id,Application_Name,App_State,Progress,Progress_State,createtime FROM `spark_status`.`appStatus` where Progress < 100 ";
                    log.Info("SelectProjectAppStatus :" + strSql);
                    lstProjectSparkJob = conn.Query<AppStatusModel>(strSql).ToList();
                }
            }
            catch (Exception ex)
            {
                string exmsg = ex.Message;

                log.Error("AppStatusModel exception :" + ex.Message.ToString());
            }
            return lstProjectSparkJob;
        }

        public Boolean UpdateReadStauts()
        {
            Encoding.RegisterProvider(CodePagesEncodingProvider.Instance);
            string Connection = Configuration["ConnectionStrings:DefaultConnection"];
            try
            {
                using (MySqlConnection conn = new MySqlConnection(Connection))
                {
                    string sql = "Update spark_status.appStatus set isRead=1 where isRead=0 and Progress_State = 'Finished' and Progress = '100' ";

                    conn.Execute(sql);
                }
                return true;
            }
            catch (Exception ex)
            {
                log.Info("UpdateProjectStauts :" + ex.Message.ToString());
                return false;
            }

        }



        public List<AppStatusModel> SelectProjAppStatusIsRead()
        {
            List<AppStatusModel> lstProjectSparkJob = null;
            try
            {
                Encoding.RegisterProvider(CodePagesEncodingProvider.Instance);
                string Connection = Configuration["ConnectionStrings:DefaultConnection"];

                using (MySqlConnection conn = new MySqlConnection(Connection))
                {
                    //var Results = db.Query<TableSqlDbType>(query, new { C1 = "10001" });
                    string strSql = "select app.id,app.Application_Id,app.Application_Name,app.App_State,app.Progress,app.Progress_State,case when app.updatetime is null then app.createtime else app.updatetime end as statustime, app.proj_id,app.dbname,app.isRead,tp.project_cht from spark_status.appStatus as app left join DeIdService.T_Project as tp on app.proj_id = tp.project_id where isRead = 1 and Progress_State = 'Finished' and Progress = '100' order by app.createtime desc";
                  //  log.Info("SelectProjAppStatus :" + strSql);
                    lstProjectSparkJob = conn.Query<AppStatusModel>(strSql).ToList();
                }
            }
            catch (Exception ex)
            {
                string exmsg = ex.Message;

                log.Error("SelectProjAppStatus exception :" + ex.Message.ToString());
            }
            return lstProjectSparkJob;
        }

        public List<AppStatusModel> SelectProjAppStatus()
        {
            List<AppStatusModel> lstProjectSparkJob = null;
            try
            {
                Encoding.RegisterProvider(CodePagesEncodingProvider.Instance);
                string Connection = Configuration["ConnectionStrings:DefaultConnection"];

                using (MySqlConnection conn = new MySqlConnection(Connection))
                {
                    //var Results = db.Query<TableSqlDbType>(query, new { C1 = "10001" });
                    string strSql = "select app.id,app.Application_Id,app.Application_Name,app.App_State,app.Progress,app.Progress_State,case when app.updatetime is null then app.createtime else app.updatetime end as statustime, app.proj_id,app.dbname,app.isRead,tp.project_cht from spark_status.appStatus as app left join DeIdService.T_Project as tp on app.proj_id = tp.project_id where isRead = 0 and Progress_State = 'Finished' and Progress = '100' order by app.createtime desc";
                   // log.Info("SelectProjAppStatus :" + strSql);
                    lstProjectSparkJob = conn.Query<AppStatusModel>(strSql).ToList();
                }
            }
            catch (Exception ex)
            {
                string exmsg = ex.Message;

                log.Error("SelectProjAppStatus exception :" + ex.Message.ToString());
            }
            return lstProjectSparkJob;
        }

        public List<ProjectSparkMan> SelectProjectJobStatus()
        {
            List<ProjectSparkMan> lstProjectSparkJob = null;
            try
            {
                Encoding.RegisterProvider(CodePagesEncodingProvider.Instance);
                string Connection = Configuration["ConnectionStrings:DefaultConnection"];

                using (MySqlConnection conn = new MySqlConnection(Connection))
                {
                    //var Results = db.Query<TableSqlDbType>(query, new { C1 = "10001" });
                    string strSql = "select tpsm.pspark_id,tpsm.app_id,tpsm.celery_id,tpsm.project_id,tp.project_name,tpsm.step,tpsm.stepstatus,tpsm.createtime,tp.Project_cht from T_Project_SparkStatus_Management as tpsm inner join T_Project as tp on tpsm.project_id=tp.project_id where tpsm.stepstatus <100 ";
                    //log.Info("SelectProjectJobStatus :" + strSql);
                    lstProjectSparkJob = conn.Query<ProjectSparkMan>(strSql).ToList();
                }
            }
            catch (Exception ex)
            {
                string exmsg = ex.Message;

               // log.Error("SelectProjectJobStatus exception :"+ex.Message.ToString());
            }
            return lstProjectSparkJob;
        }

        public List<ProjectSparkMan> SelectProjectJobStatusbyId(int pid,string steps)
        {
            List<ProjectSparkMan> lstProjectSparkJob = null;
            try
            {
                Encoding.RegisterProvider(CodePagesEncodingProvider.Instance);
                string Connection = Configuration["ConnectionStrings:DefaultConnection"];

                using (MySqlConnection conn = new MySqlConnection(Connection))
                {
                    //var Results = db.Query<TableSqlDbType>(query, new { C1 = "10001" });
                    string strSql = "select tpsm.app_id,tpsm.celery_id,tpsm.project_id,tp.project_name,tpsm.step,tpsm.stepstatus,tpsm.createtime from T_Project_SparkStatus_Management as tpsm inner join T_Project as tp on tpsm.project_id=tp.project_id where tpsm.project_id=@project_id and tpsm.step=@step and tpsm.stepstatus =100 ";
                    var datas = new ProjectSparkMan { project_id = pid, step=steps };
                    lstProjectSparkJob = conn.Query<ProjectSparkMan>(strSql,datas).ToList();
                }
            }
            catch (Exception ex)
            {
                string exmsg = ex.Message;
                log.Error("SelectProjectJobStatusbyId Exception :"+exmsg);

            }
            return lstProjectSparkJob;
        }
        public List<ProjectList> SelectProjectList(string sql)
        {
            //DataTable dt = new DataTable();
            List<ProjectList> prolist = new List<ProjectList>();
            
            Encoding.RegisterProvider(CodePagesEncodingProvider.Instance);
            string Connection = Configuration["ConnectionStrings:DefaultConnection"];
            try
            {
                MySqlConnection conn = new MySqlConnection(Connection);

                var list = conn.Query<ProjectList>(sql);
                foreach (var item in list)
                {
                    ProjectList IprolistInfo = new ProjectList();
                    IprolistInfo.project_id = item.project_id;
                    IprolistInfo.project_name = item.project_name;
                    IprolistInfo.project_status = item.project_status;
                    IprolistInfo.project_desc = item.project_desc;
                    IprolistInfo.project_cht = item.project_cht;
                    IprolistInfo.projecttime = item.projecttime;
                    IprolistInfo.useraccount = item.useraccount;
                    IprolistInfo.isML = item.isML;
                    prolist.Add(IprolistInfo);
                }
                return prolist;
            }
            catch (Exception ex)
            {
                log.Error("SelectProjectList Exception :"+ex.Message);
                return prolist;
            }

        }
    }
}
