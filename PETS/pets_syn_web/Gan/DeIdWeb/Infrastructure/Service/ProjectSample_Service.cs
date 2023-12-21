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
using System.Threading.Tasks;

namespace DeIdWeb.Infrastructure.Service
{
    public class ProjectSample_Service
    {
        public static IConfiguration Configuration { get; set; }
        private ILog log = LogManager.GetLogger(Startup.repository.Name, typeof(ProjectSample_Service));

        public ProjectSample_Service()
        {
            var builder = new ConfigurationBuilder()
            .SetBasePath(Directory.GetCurrentDirectory())
            .AddJsonFile("appsettings.json");
            Configuration = builder.Build();
        }
        public List<ProjectSampleDBData> SelectProjSampleTBKchek(string project_id,string pname)
        {
            List<ProjectSampleDBData> lstSampleDBlist = null;
            try
            {
                Encoding.RegisterProvider(CodePagesEncodingProvider.Instance);
                string Connection = Configuration["ConnectionStrings:DefaultConnection"];

                using (MySqlConnection conn = new MySqlConnection(Connection))
                {
                    //var Results = db.Query<TableSqlDbType>(query, new { C1 = "10001" });
                    string strSql = "select  ps_id,finaltblName from T_Project_SampleTable where project_id = @project_id and pro_db=@pro_db";
                    log.Info("Project Id :" + project_id);
                    log.Info("Project Name :" + pname);
                    log.Info("SelectProjSampleTB  :" + strSql);
                    lstSampleDBlist = conn.Query<ProjectSampleDBData>(strSql, new { project_id = project_id , pro_db =pname}).ToList();
                }
            }
            catch (Exception ex)
            {
                string exmsg = ex.Message;
                log.Error("SelectProjSampleTBKchek Exception:" + exmsg);

            }
            return lstSampleDBlist;
        }

        public List<ProjectSampleDBData> SelectProjSampleJobTB(string project_id,string jobname)
        {
            List<ProjectSampleDBData> lstSampleDBlist = null;
            try
            {
                Encoding.RegisterProvider(CodePagesEncodingProvider.Instance);
                string Connection = Configuration["ConnectionStrings:DefaultConnection"];

                using (MySqlConnection conn = new MySqlConnection(Connection))
                {
                    //var Results = db.Query<TableSqlDbType>(query, new { C1 = "10001" });
                    string strSql = "select tpst.project_id,tpst.pro_db,tpst.pro_tb,tpst.pro_col_en,tpst.pro_col_cht,tpst.pro_path,tpst.tableCount,tpst.tableDisCount,tpst.minKvalue,tpst.supRate,tpst.supCount,tpst.finaltblName ,tpsd.data" +
                        ",tpst.after_col_cht,tpst.after_col_en,tpst.qi_col,tpst.tablekeycol,tpst.after_col_value,tpst.gen_qi_settingvalue,tpst.warning_col " +
                        "from T_Project_SampleTable as tpst " +
                        "inner join T_Project as tp on tpst.project_id = tp.project_id and tpst.pro_db = tp.project_name " +
                        "inner join T_ProjectSampleData as tpsd on tpst.project_id = tpsd.project_id and tpst.pro_db = tpsd.dbname and  tpsd.tbname=tpst.pro_tb " +
                        "inner join T_ProjectJobStatus as tpjs on tpst.project_id = tpjs.project_id and tpst.finaltblName=tpjs.job_tb " +
                        "where tpst.project_id = @project_id and tpjs.project_jobstatus=0  and tpjs.jobrule=@jobname ";
                    log.Info("Project Id :" + project_id);
                    log.Info("SelectProjSampleTB  :" + strSql);
                    log.Info("jobname  :" + jobname);
                    lstSampleDBlist = conn.Query<ProjectSampleDBData>(strSql, new { project_id = project_id,jobname=jobname }).ToList();
                }
            }
            catch (Exception ex)
            {
                string exmsg = ex.Message;
                log.Error("SelectProjSampleTB Exception:" + exmsg);

            }
            return lstSampleDBlist;
        }

        public List<ProjectSample5Data> SelectProjSample5TB(string project_id)
        {
            List<ProjectSample5Data> lstSampleDBlist = null;
            try
            {
                Encoding.RegisterProvider(CodePagesEncodingProvider.Instance);
                string Connection = Configuration["ConnectionStrings:DefaultConnection"];

                using (MySqlConnection conn = new MySqlConnection(Connection))
                {
                    //var Results = db.Query<TableSqlDbType>(query, new { C1 = "10001" });
                    string strSql = "select tpsd.user_id,tpsd.id,tpct.pro_col_en_nunique,tpsd.project_id,tpsd.pro_name,tpsd.file_name,tpsd.data,tpsd.select_colNames, " +
                        " tpsd.targetCols,tpsd.createtime,tpsd.updatetime,tp.project_name,tpct.pro_col_en,tpct.pro_col_cht,tpct.tableCount,tpct.ob_col,tpct.ID_column,tpsd.select_data  " +
                        " from  T_ProjectSample5Data as tpsd left join T_Project as tp on tpsd.project_id = tp.project_id " +
                        " inner join T_ProjectColumnType as tpct on tpsd.project_id = tpct.project_id where tpsd.project_id = @project_id";
                    log.Info("Project Id :" + project_id);
                    log.Info("SelectProjSampleTB  :" + strSql);
                    lstSampleDBlist = conn.Query<ProjectSample5Data>(strSql, new { project_id = project_id }).ToList();
                }
            }
            catch (Exception ex)
            {
                string exmsg = ex.Message;
                log.Error("ProjectSample5Data Exception:" + exmsg);

            }
            return lstSampleDBlist;
        }


        public List<UtilityResult> SelectUtiltyResult(int pid)
        {
            List<UtilityResult> lstSampleDBlist = null;
            try
            {
                Encoding.RegisterProvider(CodePagesEncodingProvider.Instance);
                string Connection = Configuration["ConnectionStrings:DefaultConnection"];

                using (MySqlConnection conn = new MySqlConnection(Connection))
                {
                    //var Results = db.Query<TableSqlDbType>(query, new { C1 = "10001" });
                    string strSql = "SELECT distinct project_id,select_csv FROM T_utilityResult where project_id = @project_id";
                    log.Info("Project Id :" + pid);
                    log.Info("T_utilityResult  :" + strSql);
                    lstSampleDBlist = conn.Query<UtilityResult>(strSql, new { project_id = pid }).ToList();
                }
            }
            catch (Exception ex)
            {
                string exmsg = ex.Message;
                log.Error("SelectUtiltyResult Exception:" + exmsg);

            }
            return lstSampleDBlist;
        }

        public List<ProjectSampleDBData> SelectProjSampleTB(string project_id)
        {
            List<ProjectSampleDBData> lstSampleDBlist = null;
            try
            {
                Encoding.RegisterProvider(CodePagesEncodingProvider.Instance);
                string Connection = Configuration["ConnectionStrings:DefaultConnection"];

                using (MySqlConnection conn = new MySqlConnection(Connection))
                {
                    //var Results = db.Query<TableSqlDbType>(query, new { C1 = "10001" });
                    string strSql = "select tpsd.user_id,tpsd.id,tpsd.project_id,tpsd.pro_name,tpsd.file_name,tpsd.data,tpsd.select_colNames," +
                        "tpsd.targetCols,tpsd.createtime,tpsd.updatetime,tp.project_name from  T_ProjectSample5Data as tpsd " +
                        "left join T_Project as tp on tpsd.project_id = tp.project_id where tpsd.project_id = @project_id";
                    log.Info("Project Id :" + project_id);
                    log.Info("SelectProjSampleTB  :"+strSql);
                    lstSampleDBlist = conn.Query<ProjectSampleDBData>(strSql, new { project_id = project_id }).ToList();
                }
            }
            catch (Exception ex)
            {
                string exmsg = ex.Message;
                log.Error("SelectProjSampleTB Exception:"+exmsg);

            }
            return lstSampleDBlist;
        }

        public List<ProjectSampleDBData> SelectProjSampleTable(string project_id,string tablename)
        {
            List<ProjectSampleDBData> lstSampleDBlist = null;
            try
            {
                Encoding.RegisterProvider(CodePagesEncodingProvider.Instance);
                string Connection = Configuration["ConnectionStrings:DefaultConnection"];

                using (MySqlConnection conn = new MySqlConnection(Connection))
                {
                    //var Results = db.Query<TableSqlDbType>(query, new { C1 = "10001" });
                    string strSql = "select tpst.project_id,tpst.pro_db,tpst.pro_tb,tpst.pro_col_en,tpst.pro_col_cht,tpst.pro_path,tpst.tableCount,tpst.tableDisCount,tpst.minKvalue,tpst.supRate,tpst.supCount,tpst.finaltblName ,tpsd.data" +
                        ",tpst.after_col_cht,tpst.after_col_en,tpst.qi_col,tpst.tablekeycol,tpst.after_col_value,tpst.gen_qi_settingvalue,tpst.warning_col from T_Project_SampleTable as tpst inner join T_Project as tp on tpst.project_id = tp.project_id and tpst.pro_db = tp.project_name inner join T_ProjectSampleData as tpsd on tpst.project_id = tpsd.project_id and tpst.pro_db = tpsd.dbname " +
                        "where tpst.project_id = @project_id and tpst.pro_tb=@pro_tb";
                    lstSampleDBlist = conn.Query<ProjectSampleDBData>(strSql, new { project_id = project_id, pro_tb=tablename }).ToList();
                }
            }
            catch (Exception ex)
            {
                string exmsg = ex.Message;
                log.Error("SelectProjSampleTable exception :"+exmsg);

            }
            return lstSampleDBlist;
        }

        public List<ProjectSampleDBData> SelectProjSampleTableByTableId(string project_id, string ps_id)
        {
            List<ProjectSampleDBData> lstSampleDBlist = null;
            try
            {
                Encoding.RegisterProvider(CodePagesEncodingProvider.Instance);
                string Connection = Configuration["ConnectionStrings:DefaultConnection"];

                using (MySqlConnection conn = new MySqlConnection(Connection))
                {
                    //var Results = db.Query<TableSqlDbType>(query, new { C1 = "10001" });
                    string strSql = "select tpst.project_id,tpst.pro_db,tpst.pro_tb,tpst.pro_col_en,tpst.pro_col_cht,tpst.pro_path,tpst.tableCount,tpst.tableDisCount,tpst.minKvalue,tpst.supRate,tpst.supCount,tpst.finaltblName ,tpsd.data" +
                        ",tpst.after_col_cht,tpst.after_col_en,tpst.qi_col,tpst.tablekeycol,tpst.after_col_value,tpst.gen_qi_settingvalue,tpst.warning_col from T_Project_SampleTable as tpst inner join T_Project as tp on tpst.project_id = tp.project_id and tpst.pro_db = tp.project_name inner join T_ProjectSampleData as tpsd on tpst.project_id = tpsd.project_id and tpst.pro_db = tpsd.dbname where tpst.project_id = @project_id and tpst.ps_id=@ps_id";
                    lstSampleDBlist = conn.Query<ProjectSampleDBData>(strSql, new { project_id = project_id, ps_id = int.Parse(ps_id) }).ToList();
                }
            }
            catch (Exception ex)
            {
                string exmsg = ex.Message;
                log.Error("SelectProjSampleTable exception :" + exmsg);

            }
            return lstSampleDBlist;
        }

        public List<ProjectSampleDBData> SelectProjSampleTablebyId(string project_id)
        {
            List<ProjectSampleDBData> lstSampleDBlist = null;
            try
            {
                Encoding.RegisterProvider(CodePagesEncodingProvider.Instance);
                string Connection = Configuration["ConnectionStrings:DefaultConnection"];

                using (MySqlConnection conn = new MySqlConnection(Connection))
                {
                    //var Results = db.Query<TableSqlDbType>(query, new { C1 = "10001" });
                    string strSql = "select tpst.project_id,tpst.pro_db,tpst.pro_tb,tpst.pro_col_en,tpst.pro_col_cht,tpst.pro_path,tpst.tableCount,tpst.tableDisCount,tpst.minKvalue,tpst.supRate,tpst.supCount,tpst.finaltblName ,tpsd.data" +
                        ",tpst.after_col_cht,tpst.after_col_en,tpst.qi_col,tpst.tablekeycol,tpst.after_col_value,tpst.gen_qi_settingvalue,tpst.warning_col from T_Project_SampleTable as tpst inner join T_Project as tp on tpst.project_id = tp.project_id and tpst.pro_db = tp.project_name inner join T_ProjectSampleData as tpsd on tpst.project_id = tpsd.project_id and tpst.pro_db = tpsd.dbname where tpst.project_id = @project_id";
                    lstSampleDBlist = conn.Query<ProjectSampleDBData>(strSql, new { project_id = project_id}).ToList();
                }
            }
            catch (Exception ex)
            {
                string exmsg = ex.Message;
                log.Error("SelectProjSampleTablebyId Exception :"+exmsg);

            }
            return lstSampleDBlist;
        }

        public bool UpdateProjectSampleTableQISetting(string proj_id,string qi_settingvalue)
        {
            Encoding.RegisterProvider(CodePagesEncodingProvider.Instance);
            string Connection = Configuration["ConnectionStrings:DefaultConnection"];
            try
            {
                using (MySqlConnection conn = new MySqlConnection(Connection))
                {
                    string sql = "Update T_Project_SampleTable set updatetime=now(), gen_qi_settingvalue=@gen_qi_settingvalue where project_id=@project_id and pro_db=(select project_name from T_Project where project_id=@project_id) ;";
                    var datas = new ProjectSampleTalbeModel { project_id = int.Parse(proj_id), gen_qi_settingvalue = qi_settingvalue };
                    conn.Execute(sql, datas);
                }
                return true;
            }
            catch (Exception ex)
            {
                log.Error("UpdateProjectSampleTableQISetting Exception : " + ex.Message);

                return false;
            }

        }

        public bool UpdateProjectSampleTableSetting(string proj_id, string tablename,string after_col,string after_colvalue,string keytable,string gen_qi_value)
        {
            Encoding.RegisterProvider(CodePagesEncodingProvider.Instance);
            string Connection = Configuration["ConnectionStrings:DefaultConnection"];
            try
            {
                using (MySqlConnection conn = new MySqlConnection(Connection))
                {
                    string sql = "Update T_Project_SampleTable set updatetime=now(),gen_qi_settingvalue=@gen_qi_settingvalue where project_id=@project_id and pro_db=(select project_name from T_Project where project_id=@project_id) and pro_tb=@pro_tb ;";
                    var datas = "";// new ProjectSampleTalbeModel { project_id = int.Parse(proj_id), minKvalue = int.Parse(kvalue), gen_qi_settingvalue = qi_settingvalue, pro_tb = tablename };
                    conn.Execute(sql, datas);
                }
                return true;
            }
            catch (Exception ex)
            {
                log.Error("UpdateProjectSampleTableQI Exception : " + ex.Message);
                return false;
            }

        }

        public bool UpdateProjectSampleTableConfig(string ps_id,string proj_id, string keytablecol, string qi_settingvalue, string after_col_en,string after_col_cht,string after_col_value,string qi_col)
        {
            Encoding.RegisterProvider(CodePagesEncodingProvider.Instance);
            string Connection = Configuration["ConnectionStrings:DefaultConnection"];
            try
            {
                using (MySqlConnection conn = new MySqlConnection(Connection))
                {
                    string sql = "Update T_Project_SampleTable set updatetime=now(),gen_qi_settingvalue=@gen_qi_settingvalue,qi_col=@qi_col,tablekeycol=@tablekeycol,after_col_cht=@after_col_cht,after_col_en=@after_col_en,after_col_value=@after_col_value where project_id=@project_id and ps_id=@ps_id ;";
                    var datas = new ProjectSampleTalbeModel { ps_id=int.Parse(ps_id),project_id = int.Parse(proj_id),gen_qi_settingvalue = qi_settingvalue,qi_col=qi_col,tablekeycol=keytablecol,after_col_cht=after_col_cht,after_col_en=after_col_en,after_col_value=after_col_value};
                    conn.Execute(sql, datas);
                }
                return true;
            }
            catch (Exception ex)
            {
                log.Error("UpdateProjectSampleTableQI Exception : " + ex.Message);
                return false;
            }

        }

        public bool UpdateProjectSampleTableQI(string proj_id,  string kvalue,string qi_settingvalue,string tablename)
        {
            Encoding.RegisterProvider(CodePagesEncodingProvider.Instance);
            string Connection = Configuration["ConnectionStrings:DefaultConnection"];
            try
            {
                using (MySqlConnection conn = new MySqlConnection(Connection))
                {
                    string sql = "Update T_Project_SampleTable set updatetime=now(), minKvalue=@minKvalue,gen_qi_settingvalue=@gen_qi_settingvalue where project_id=@project_id and pro_db=(select project_name from T_Project where project_id=@project_id) and pro_tb=@pro_tb ;";
                    var datas = new ProjectSampleTalbeModel { project_id = int.Parse(proj_id), minKvalue=int.Parse(kvalue), gen_qi_settingvalue = qi_settingvalue,pro_tb=tablename };
                    conn.Execute(sql, datas);
                }
                return true;
            }
            catch (Exception ex)
            {
                log.Error("UpdateProjectSampleTableQI Exception : "+ex.Message);
                return false;
            }

        }

        public bool UpdateProjectSampleTableSettingValue(string proj_id, string after_col_en, string after_col_cht, string after_col_qi, string tablekeycol, string selectvalue, string qi_settingvalue, string tablename,string isqi)
        {
            Encoding.RegisterProvider(CodePagesEncodingProvider.Instance);
            string Connection = Configuration["ConnectionStrings:DefaultConnection"];
            try
            {
                using (MySqlConnection conn = new MySqlConnection(Connection))
                {
                    string sql = "Update T_Project_SampleTable set after_col_en=@after_col_en,after_col_cht=@after_col_cht,qi_col=@qi_col,tablekeycol=@tablekeycol,updatetime=now(),after_col_value=@after_col_value,gen_qi_settingvalue=@gen_qi_settingvalue,isqi=@isqi where project_id=@project_id and pro_db=(select project_name from T_Project where project_id=@project_id) and pro_tb=@pro_tb ;";
                    var datas = new ProjectSampleTalbeModel { project_id = int.Parse(proj_id), after_col_en = after_col_en, after_col_cht = after_col_cht, qi_col = after_col_qi, tablekeycol = tablekeycol, after_col_value = selectvalue, gen_qi_settingvalue= qi_settingvalue ,pro_tb = tablename,isqi=isqi };
                    conn.Execute(sql, datas);
                }
                return true;
            }
            catch (Exception ex)
            {
                log.Error("UpdateProjectSampleTable Exception :" + ex.Message);
                return false;
            }

        }

        public bool UpdateProjectSampleTable(string proj_id, string after_col_en, string after_col_cht,string after_col_qi,string tablekeycol,string selectvalue,string qi_settingvalue,string tablename)
        {
            Encoding.RegisterProvider(CodePagesEncodingProvider.Instance);
            string Connection = Configuration["ConnectionStrings:DefaultConnection"];
            try
            {
                using (MySqlConnection conn = new MySqlConnection(Connection))
                {
                    string sql = "Update T_Project_SampleTable set after_col_en=@after_col_en,after_col_cht=@after_col_cht,qi_col=@qi_col,tablekeycol=@tablekeycol,updatetime=now(),after_col_value=@after_col_value where project_id=@project_id and pro_db=(select project_name from T_Project where project_id=@project_id) and pro_tb=@pro_tb ;";
                    var datas = new ProjectSampleTalbeModel { project_id=int.Parse(proj_id),after_col_en= after_col_en, after_col_cht= after_col_cht, qi_col = after_col_qi, tablekeycol = tablekeycol,after_col_value=selectvalue , pro_tb=tablename };
                    conn.Execute(sql, datas);
                }
                return true;
            }
            catch (Exception ex)
            {
                log.Error("UpdateProjectSampleTable Exception :"+ex.Message);
                return false;
            }

        }

        public List<ProjectSampleTalbeModel> SelectProjSampleDataTB(string project_id)
        {
            List<ProjectSampleTalbeModel> lstSampleDBlist = null;
            try
            {
                Encoding.RegisterProvider(CodePagesEncodingProvider.Instance);
                string Connection = Configuration["ConnectionStrings:DefaultConnection"];

                using (MySqlConnection conn = new MySqlConnection(Connection))
                {
                    //var Results = db.Query<TableSqlDbType>(query, new { C1 = "10001" });
                    string strSql = "select tpst.project_id,tpst.pro_db,tpst.pro_tb,tpst.pro_col_en,tpst.pro_col_cht,tpst.pro_path,tpst.tableCount,tpst.tableDisCount,tpst.minKvalue,tpst.supRate,tpst.supCount,tpst.finaltblName ,tpsd.data from T_Project_SampleTable as tpst " +
                        "inner join T_Project as tp on tpst.project_id = tp.project_id and tpst.pro_db = tp.project_name inner join T_ProjectSampleData as tpsd on tpst.project_id = tpsd.project_id and tpst.pro_db = tpsd.dbname where tpst.project_id = @project_id";
                    lstSampleDBlist = conn.Query<ProjectSampleTalbeModel>(strSql, new { project_id = project_id }).ToList();
                }
            }
            catch (Exception ex)
            {
                string exmsg = ex.Message;


            }
            return lstSampleDBlist;
        }
    }
}
