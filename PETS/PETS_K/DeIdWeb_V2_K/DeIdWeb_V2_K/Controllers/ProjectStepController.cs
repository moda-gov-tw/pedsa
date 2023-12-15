using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using DeIdWeb_V2_K.Infrastructure.Service;
using DeIdWeb_V2_K.Models;
using Newtonsoft.Json;
using Microsoft.AspNetCore.Mvc;
using Newtonsoft.Json.Linq;
using System.IO;
using log4net;
using DeIdWeb_V2_K.Filters;
using Resources;
using Microsoft.AspNetCore.Http;
using System.Web;
using Microsoft.AspNetCore.Authorization;
using System.Security.Claims;
using DeIdWeb_V2_K.Infrastructure.Reposiotry;
//using Microsoft.AspNetCore.Mvc.ViewFeatures;

namespace DeIdWeb_V2_K.Controllers
{
    [TypeFilter(typeof(CultureFilter))]
    [AutoValidateAntiforgeryToken]//
    [ResponseCache(NoStore = true)]
    public class ProjectStepController : Controller
    {
        public HttpHelper httphelp = new HttpHelper();
        public MySqlDBHelper mydbhelper = new MySqlDBHelper();
        public ProjectStatus_Service psService = new ProjectStatus_Service();
        public ProjectSample_Service ps_Service = new ProjectSample_Service();
        public SystemLog_Service syslog_service = new SystemLog_Service();
        public GenSettingRandomData genRandim = new GenSettingRandomData();
        //
        private ILog log = LogManager.GetLogger(Startup.repository.Name, typeof(ProjectStepController));

        private readonly ILocalizer _localizer;

        public ProjectStepController(ILocalizer localizer)
        {
            _localizer = localizer;
        }
        //[Authorize]
        public IActionResult Step1(string proj_id, string project_name, string stepstatus, string project_cht) //import
        {
            ViewData["Project_cht"] = project_cht;
            ViewData["ProjectName"] = project_name;
            ViewData["ProjectId"] = proj_id;
            ViewData["ProjectStep"] = stepstatus;
            ViewData["file"] ="";//"專案資料夾無資料";
            mydbhelper.UpdateProjectStauts(int.Parse(proj_id), 1, "資料匯入處理");
            if (stepstatus == "1")
            {
                //確認狀態與更新
                var jobstatusresult = mydbhelper.SelectProjectJobStatusByProject(proj_id, "ImportFile");
                if (jobstatusresult.Count > 0)
                {
                    foreach (var item in jobstatusresult)
                    {
                        APISparkJobModel sparkmodel = new APISparkJobModel
                        {
                            applicationID = item.app_id
                        };
                        string strsparkstatus = JsonHelper.SerializeObject(sparkmodel);
                        // string pythonstr = "{\"projName\": \"test_import_all\", \"projStep\": \"getServerFolder\", \"projID\": \"1\"}";
                        byte[] bytespark = Encoding.GetEncoding("utf-8").GetBytes(strsparkstatus);

                        //參數編成 Base64 字串
                        string JsonServer = Convert.ToBase64String(bytespark);

                        APIModel apiModel = new APIModel
                        {
                            jsonBase64 = JsonServer
                        };

                        string strapi = JsonHelper.SerializeObject(apiModel);
                        //var apirestult=HttpHelper.PostUrl("getServerFolder", "{\"jsonBase64\":\"eyJwcm9qTmFtZSI6ICJ0ZXN0X2ltcG9ydF9hbGwiLCAicHJvalN0ZXAiOiAiZ2V0U2VydmVyRm9sZGVyIiwgInByb2pJRCI6ICIxIn0=\"}");                
                        var apirestult = HttpHelper.PostUrl("getSparkJobStatusB64", strapi);

                        JObject apiresultJsobj = JObject.Parse(apirestult);
                        string apibase641 = apiresultJsobj["jsonBase64"].ToString();
                        var jsapiresults = Encoding.UTF8.GetString(Convert.FromBase64String(apibase641));
                        if (jsapiresults.Length > 2)
                        {
                            JObject apidecode = JObject.Parse(jsapiresults);
                            //"{\"Start-Time\": \"1550301766251\", \"Application-Id\": \"application_1550199357248_0040\", \"Final-State\": \"SUCCEEDED\", 
                            //\"State\": \"FINISHED\", \"Progress\": \"100%\", \"Finish-Time\": \"1550301786413\"}"
                            string apistatus = apidecode["Final-State"].ToString();
                            if (apistatus == "SUCCEEDED")
                            {
                                string process = apidecode["Progress"].ToString().Replace("%", "");
                                //更新SparkMan 狀態與Project 狀態

                                var sparkupdate = psService.UpdateProjectSparkStauts(item.pspark_id, item.app_id, process);
                                if (sparkupdate)
                                {
                                    //project
                                    var prostatus = mydbhelper.UpdateProjectStauts(int.Parse(proj_id), 2, "資料匯入中");
                                    if (prostatus)
                                    {
                                        ViewData["ProjectStep"] = "2";
                                    }
                                }
                                else
                                {
                                    //spark update error
                                }
                            }
                        }

                    }
                }
                else //if (jobstatusresult.Count == 0)
                {
                    //如果無資料
                    log.Info("Step1 Job no data ");
                    var pstatus = psService.SelectProjectStatuis(int.Parse(proj_id));
                    if (pstatus.Count > 0)
                    {
                        foreach (var item in pstatus)
                        {
                            ViewData["ProjectStep"] = item.project_status;
                        }

                    }
                }
                //returnmsg = jobstatusresult.Count.ToString();
            }

            string sql = "select * from T_Project where project_id=" + proj_id + " and project_name='" + project_name + "'";
            try
            {
                var prolist = mydbhelper.SelectProject(sql);
                foreach (var item in prolist)
                {
                    ViewData["ProjectDesc"] = item.Project_desc;
                }

                //"{\"projName\": \"test_import_all\", \"projStep\": \"getServerFolder\", \"projID\": \"1\"}"

                GetServerFolderJsonModel serverfolder = new GetServerFolderJsonModel
                {
                    projName = project_name,
                    //serverfolder.projName = "test_import_all";
                    projStep = "getServerFolder",
                    projID = proj_id
                };
                //serverfolder.projID = "1";
                //jsonDic_ = {
                //    'projID': '7',
                //   'projStep': 'getServerFolder',
                //   'projName': '2QDataMarketDeid'}
                //string jsonDic_ = "{\"projName\": \"2QDataMarketDeId\", \"projStep\": \"getServerFolder\", \"projID\": \"7\"}";
                string serverfolderstr = JsonHelper.SerializeObject(serverfolder);
                log.Info("getServerFolder :" + serverfolderstr);
                //  string serverfolderstr = JsonHelper.SerializeObject(serverfolder);
                string jsondic = JsonHelper.SerializeObject(serverfolderstr);
                //  string pythonstr = "{\"projName\": \"test_import_all\", \"projStep\": \"getServerFolder\", \"projID\": \"1\"}";
                //byte[] byteServer = Encoding.GetEncoding("utf-8").GetBytes(serverfolderstr);
                byte[] byteServer = Encoding.GetEncoding("utf-8").GetBytes(serverfolderstr);

                //參數編成 Base64 字串
                string JsonServer = Convert.ToBase64String(byteServer);

                APIModel apiModel = new APIModel();
                apiModel.jsonBase64 = JsonServer;

                string strapi = JsonHelper.SerializeObject(apiModel);
                //var apirestult=HttpHelper.PostUrl("getServerFolder", "{\"jsonBase64\":\"eyJwcm9qTmFtZSI6ICJ0ZXN0X2ltcG9ydF9hbGwiLCAicHJvalN0ZXAiOiAiZ2V0U2VydmVyRm9sZGVyIiwgInByb2pJRCI6ICIxIn0=\"}");                
                var apirestult = HttpHelper.PostUrl("getServerFolder", strapi);
                log.Info("getServerFolder return base64:" + apirestult);
                //var oldapiresult = "eyJzdGF0dXMiOiAtMSwgImZvbGRlcnMiOiAiIiwgImVyck1zZyI6ICJDYW5ub3QgZmluZCBhbnkgZmlsZXMgaW4gdGhpcyBwcm9qZWN0In0=";
                //var oldapiresult = "eyJwcm9qTmFtZSI6ICIyUURhdGFNYXJrZXREZUlkIiwgInByb2pTdGVwIjogImdlbiIsICJwcm9qSUQiOiAiMSIsICJtYWluSW5mbyI6IHsidGJsXzEiOiB7ImNvbEluZm8iOiB7ImNvbF8xIjogeyJjb2xOYW1lIjogImNfMjczN18xIiwgImFwaU5hbWUiOiAiZ2V0R2VuTnVtTGV2ZWwiLCAidXNlclJ1bGUiOiAiMTAifSwgImNvbF82IjogeyJjb2xOYW1lIjogImNfMjczN182IiwgImFwaU5hbWUiOiAiZ2V0R2VuVWRmIiwgInVzZXJSdWxlIjogIi9hcHAvYXBwL2RldnAvdWRmUnVsZS8ycWRhdGFtYXJrZXRkZWlkL3VkZm1hY3VpZF9hZHVsdF9pZC9tYXJpdGFsX3N0YXR1c19ydWxlLnR4dCJ9LCAiY29sXzExIjogeyJjb2xOYW1lIjogImNfMjczN18xMSIsICJhcGlOYW1lIjogImdldEdlbk51bUxldmVsIiwgInVzZXJSdWxlIjogIjUwIn0sICJjb2xfMTIiOiB7ImNvbE5hbWUiOiAiY18yNzM3XzEyIiwgImFwaU5hbWUiOiAiZ2V0R2VuTnVtTGV2ZWwiLCAidXNlclJ1bGUiOiAiMTAwIn0sICJjb2xfMTMiOiB7ImNvbE5hbWUiOiAiY18yNzM3XzEzIiwgImFwaU5hbWUiOiAiZ2V0R2VuTnVtSW50ZXJ2YWwiLCAidXNlclJ1bGUiOiAiMV8xMF81XjExXzIwXzE1XjIxXzEwMF8yNSJ9fSwgInRibE5hbWUiOiAidWRmTWFjVUlEX2FkdWx0X2lkIiwgImNvbF9lbiI6ICJjXzI3MzdfMCxjXzI3MzdfMSxjXzI3MzdfMixjXzI3MzdfMyxjXzI3MzdfNCxjXzI3MzdfNSxjXzI3MzdfNixjXzI3MzdfNyxjXzI3MzdfOCxjXzI3MzdfOSxjXzI3MzdfMTAsY18yNzM3XzExLGNfMjczN18xMixjXzI3MzdfMTMsY18yNzM3XzE0LGNfMjczN18xNSJ9fX0=";
                JObject apiresultJsobj = JObject.Parse(apirestult);
                string apibase64 = apiresultJsobj["jsonBase64"].ToString();
                var jsapiresult = Encoding.UTF8.GetString(Convert.FromBase64String(apibase64));
                var newjsonresult = jsapiresult.Replace("\\", "");
                var xd = jsapiresult.Length;
                var xz = newjsonresult.Length;
                log.Info("getServerFolder return :" + jsapiresult);
                JObject apidecode = JObject.Parse(jsapiresult);
                string apistatus = apidecode["status"].ToString();
                if (apistatus == "1")
                {
                    string apiserverfolder = apidecode["folders"].ToString();
                    var folderarray = apiserverfolder.Split(';');
                    string showfile = "";
                    if (folderarray.Length > 0)
                    {
                        for (int i = 0; i < folderarray.Length; i++)
                        {
                            string folderpath = folderarray[i].ToString();
                            var filename = Path.GetFileName(folderpath);
                            showfile += filename + ",";
                        }
                        showfile = showfile.Substring(0, showfile.Length - 1);
                    }
                    ViewData["file"] = showfile;
                }
                else
                {
                    ViewData["file"] = "";
                }
            }
            catch (Exception ex)
            {
                log.Error("Step1 :" + ex.Message);
            }
            return View();
        }

        public IActionResult AddPartner() //import
        {


            return View();
        }

       // [Authorize]
        public IActionResult Step2(string proj_id, string project_name,string project_cht,string loginname,string returnurl) //setting 間接識別欄位
        {
            ViewData["Project_cht"] = project_cht;
            ViewData["ProjectId"] = proj_id;
            ViewData["ProjectName"] = project_name;
            ViewBag.LoginName = loginname;
            List<ProjectSampleDBData> lstST = null;
            ViewData["projectstatus"] = "";
            ViewData["returnurl"] = returnurl;
            ViewData["loginname"] = loginname;
            log.Info("Step2 return url  :" + returnurl);
            log.Info("Step2 loginname  :" + loginname);

            try
            {
                var lstpss = psService.SelectProjectStatuis(int.Parse(proj_id));
                if (lstpss.Count > 0)
                {
                    string psStatus = "";
                    foreach (var item in lstpss)
                    {
                        psStatus = item.project_status.ToString();
                    }

                    if (int.Parse(psStatus) > 2)
                    {
                        ViewData["projectstatus"] = psStatus;
                    }
                }

                string colname = "";
                string colname_cht = "";
                string selectTable = "";
                //  ViewData["tbData"] = "";
                // part 1 select sampletable
                lstST = ps_Service.SelectProjSampleTB(proj_id);
                log.Info("Step2 DataRow Count :" + lstST.Count());
                if (lstST.Count > 0)
                {
                    int x = 1;
                    foreach (var item in lstST)
                    {
                        //     JObject apidecode = JObject.Parse(item.data.ToString());
                        selectTable = item.pro_tb;
                        //ViewData["tbData"] = item.data.ToString();
                        string vdname = "tbData_" + x.ToString();
                        string colen = "colen_" + x.ToString();
                        ViewData[vdname] = item.data.ToString();
                        ViewData[colen] = item.pro_col_en.ToString();
                        if (item.after_col_en == null)
                        {
                            colname = item.pro_col_en.ToString();
                            colname_cht = item.pro_col_cht;
                            //ViewData["colname"] = "[" + colname_cht + "]";
                        }
                        else
                        {
                            colname = item.after_col_en.ToString();
                            colname_cht = item.after_col_cht;
                            // ViewData["colname"] = "[" + colname_cht + "]";
                        }

                        //ViewData["colen"] = item.pro_col_en;
                        x++;
                    }
                }
                // part 2 select sampleData
            }
            catch (Exception ex)
            {
                log.Error("Step2 Exception :" + ex.Message.ToString());
            }
            return View(lstST);
        }

     //   [Authorize]
        public IActionResult Step5(string proj_id, string project_name,string project_cht) //setting 間接識別欄位
        {
            ViewData["Project_cht"] = project_cht;
            ViewData["ProjectId"] = proj_id;
            ViewData["ProjectName"] = project_name;
            //ViewData["Project_Cht"] = project_cht;
            ViewData["ganselect_data"] = "";
            ViewData["ganselect_colname"] = "";
            List<ProjectSampleDBData> lstST = null;
            ViewData["projectstatus"] = "";
            try
            {
                var lstpss = psService.SelectProjectStatuis(int.Parse(proj_id));
                if (lstpss.Count > 0)
                {
                    string psStatus = "";
                    foreach (var item in lstpss)
                    {
                        psStatus = item.project_status.ToString();
                    }

                    if (int.Parse(psStatus) > 2)
                    {
                        ViewData["projectstatus"] = psStatus;
                    }
                }
                ViewData["ob_col_str"] = "";
                ViewData["col_data"] = "";
                ViewData["filename"] = "";
                string colname = "";
                string colname_cht = "";
                string selectTable = "";
                //  ViewData["tbData"] = "";
                // part 1 select sampletable
                lstST = ps_Service.SelectProjSampleTB(proj_id);
                log.Info("Step2 DataRow Count :" + lstST.Count());
                if (lstST.Count > 0)
                {
                    int x = 1;
                    foreach (var item in lstST)
                    {
                        //     JObject apidecode = JObject.Parse(item.data.ToString());
                        selectTable = item.finaltblName;
                        //ViewData["tbData"] = item.data.ToString();
                        string vdname = "tbData_" + x.ToString();
                        string colen = "colen_" + x.ToString();
                        string discolen = "discolen_" + x.ToString();
                        ViewData["id_col"] = "";
                        ViewData["ganselect_data"] = item.pro_col_cht;
                        ViewData["ganselect_colname"] = item.pro_col_cht;
                        ViewData["filename"] = item.pro_tb;
                        ViewData["col_data"] = item.pro_col_cht;
                        //ViewData["old_idcol"] = item.ID_Column.ToString();
                        //ViewData["ob_col_str"] = item.ob_col.ToString();
                        //var id_col = item.ID_Column.ToString();
                        ViewData[discolen] = 0;
                        if (item.distinctCount == null)
                        {
                            ViewData[discolen] = 0;
                        }
                        else
                        {
                            ViewData[discolen] = item.distinctCount.ToString();
                        }
                        ViewData[vdname] = item.kdata;
                        ViewData[colen] = item.ToString();
                        if (item.pro_col_en == null)
                        {
                            colname = item.pro_col_cht.ToString();
                            colname_cht = item.pro_col_cht;
                            //ViewData["colname"] = "[" + colname_cht + "]";
                        }
                        else
                        {
                            colname = item.pro_col_cht.ToString();
                            colname_cht = item.pro_col_cht;
                            // ViewData["colname"] = "[" + colname_cht + "]";
                        }

                        //ViewData["colen"] = item.pro_col_en;
                        x++;
                    }
                }
                // part 2 select sampleData
            }
            catch (Exception ex)
            {
                log.Error("Step5 Exception :" + ex.Message.ToString());
            }
            return View(lstST);
        }

        //public IActionResult UpdateDate()
       // [Authorize]
        public IActionResult Step3(string proj_id, string project_name,string project_cht, string loginname, string returnurl)
        {
            ViewData["Project_cht"] = project_cht;
            ViewData["ProjectId"] = proj_id;
            ViewData["ProjectName"] = project_name;
            ViewBag.LoginName = loginname;
            ViewData["returnurl"] = returnurl;
            ViewData["loginname"] = loginname;
            log.Info("Step2 return url  :" + returnurl);
            log.Info("Step2 loginname  :" + loginname);
            log.Info("Project Id :" + proj_id);
            log.Info("Project Name :" + project_name);
            log.Info("Step3 return url  :" + returnurl);
            List<ProjectSampleDBData> lstST = null;
            try
            {
                //string colname = "";
                string colqi = "";
                string mink = "";
                string T1 = "";
                string T2 = "";
                string r_value = "";
                //string mink = "";
                //  ViewData["tbData"] = "";
                // part 1 select sampletable
                lstST = ps_Service.SelectProjSampleTB(proj_id);
                if (lstST.Count > 0)
                {
                    foreach (var item in lstST)
                    {
                        //ViewData["tbName"] = item.pro_tb;

                        //     JObject apidecode = JObject.Parse(item.data.ToString());
                        //ViewData["tbData"] = item.data.ToString();
                        //colname = item.after_col_cht.ToString();
                        ///ViewData["colen"] = item.after_col_en;
                        //ViewData["colcht"] = colname;
                        mink = item.minKvalue.ToString();
                        colqi = item.qi_col;
                        if (item.T1.ToString() != "")
                        {
                            var strt1 = item.T1.ToString();
                            var new_t1 = decimal.Round(Decimal.Parse(strt1), 2);
                            T1 = new_t1.ToString();
                        }
                        else
                        {
                            T1 = item.T1.ToString();
                        }

                        if (item.T2.ToString() != "")
                        {
                            var strt2 = item.T2.ToString();
                            var new_t2 = decimal.Round(Decimal.Parse(strt2), 2);
                            T2 = new_t2.ToString();
                        }
                        else
                        {
                            T2 = item.T2.ToString();
                        }

                        if (item.r_value.ToString() != "")
                        {
                            var strr_value = item.r_value.ToString();
                            var new_rvalue = decimal.Round(Decimal.Parse(strr_value), 2);
                            r_value = new_rvalue.ToString();
                        }
                        else
                        {
                            r_value = item.r_value.ToString();
                        }
                        


                        //  ViewData["colcht"] = "[" + item.after_col_cht + "]";
                    }
                }
                var colarray = colqi.Split(",");
                string newcol = "";
                for (int i = 0; i < colarray.Length; i++)
                {
                    var qiarr = colarray[i].Split('-');
                    newcol += qiarr[0] + ",";
                }
                ViewData["all_qi"] = colqi;
                newcol = newcol.Substring(0, newcol.Length - 1);
                //newcol = newcol;
                // part 2 select sampleData
                ViewData["colqi"] = newcol;
                ViewData["mink"] = mink;
                ViewData["r_value"] = r_value;
                ViewData["T2"] = T2;
                ViewData["T1"] = T1;
            }
            catch (Exception ex)
            {
                log.Error("Step3 Exception :" + ex.Message);
            }
            return View(lstST);

        }
    
        private string GetQIValueSelectName(string selectvalue)
        {
            string getQiSelectName = "";
            switch (selectvalue)
            {
                case "請選擇":
                    getQiSelectName = "請選擇";
                    break;
                case "0":
                    getQiSelectName = "請選擇";
                    break;
                case "1":
                    getQiSelectName = "地址";
                    break;
                case "2":
                    getQiSelectName = "日期";
                    break;
                case "3":
                    getQiSelectName = "擷取字串";
                    break;
                case "4":
                    getQiSelectName = "數字大區間";
                    break;
                case "5":
                    getQiSelectName = "數字小區間";
                    break;
                case "6":
                    getQiSelectName = "數字區間含上下界";
                    break;
                case "7":
                    getQiSelectName = "不處理";
                    break;
                case "8":
                    getQiSelectName = "Hash";
                    break;
                case "9":
                    getQiSelectName = "離群值處理";
                    break;
            }
            return getQiSelectName;
        }

        private string GetQiSelectNameLevel2(string selectvalue, string selectlevel2)
        {
            string getQiSelectName = "";
            switch (selectvalue)
            {
                case "請選擇":
                    getQiSelectName = "請選擇";
                    break;
                case "0":
                    getQiSelectName = "請選擇";
                    break;
                case "1":
                    getQiSelectName = "地址";
                    break;
                case "2":
                    getQiSelectName = "日期";
                    break;
                case "3":
                    getQiSelectName = "擷取字串";
                    break;
                case "4":
                    getQiSelectName = "數字大區間";
                    break;
                case "5":
                    getQiSelectName = "數字小區間";
                    break;
                case "6":
                    getQiSelectName = "數字區間含上下界";
                    break;
                case "7":
                    getQiSelectName = "不處理";
                    break;
                case "8":
                    getQiSelectName = "Hash";
                    break;
                case "9":
                    getQiSelectName = "離群值處理";
                    break;
            }
            return getQiSelectName;
        }
        //[Authorize]
        public IActionResult Step3_2(string proj_id, string project_name, string kvalue, string base64selectqi,string project_cht, string loginname, string returnurl)
        {
           
            var selectqicountvalue = base64selectqi; //HttpUtility.ParseQueryString(base64selectqi).ToString();
            ViewData["Project_cht"] = project_cht;
            ViewBag.LoginName = loginname;
            ViewData["returnurl"] = returnurl;
            ViewData["loginname"] = loginname;
            log.Info("Step2 return url  :" + returnurl);
            log.Info("Step2 loginname  :" + loginname);
            ViewData["ProjectId"] = proj_id;
            ViewData["ProjectName"] = project_name;
            ViewData["tbName"] = "";
            ViewData["kvalue"] = "";
            ViewData["r_value"] = "";
            ViewData["T1"] = "";
            ViewData["T2"] = "";
            ViewData["tbcount"] = "";
            List<ProjectSampleDBData> lst = null;
            ViewData["selectqivalue"] = "";
            ViewData["selectqigenvalue"] = "";
            ViewData["gensparkstatus"] = "";
            ViewData["pro_tb"] = "";
            string newkvalue = "";
            string newselectqi = "";
            log.Info("Step3_2 Project_Id :" + proj_id);
            log.Info("Step3_2 ProjectName :" + project_name);
            log.Info("Step3_2 kvalue :" + kvalue);
            log.Info("Step3_2 selectqicountvalue :" + selectqicountvalue);
            ViewData["r_value"] = "0";
            ViewData["T1"] = "0";
            ViewData["T2"] = "0";
            //if (new_rtvalue != null && new_rtvalue !="")
            //{
            //    var rtvalue_arr = new_rtvalue.Split(',');
            //    if (rtvalue_arr.Length >= 3)
            //    {
            //        ViewData["r_value"] = rtvalue_arr[0].ToString();
            //        ViewData["T1"] = rtvalue_arr[1].ToString();
            //        ViewData["T2"] = rtvalue_arr[2].ToString();
            //    }
            //}


            string table_html = "";
            //select sparkstatus
            var jobstatusresult100 = mydbhelper.SelectProjectJobStatusbyId(int.Parse(proj_id), "Gen");
            if (jobstatusresult100.Count > 0)
            {
                //  return Redirect("User/News");
                log.Info(" Step3_2  Gen Finish Redirect to Step4:" + kvalue);

                return RedirectToAction("Step4", "ProjectStep", new { proj_id, project_name });
            }
            else
            {

                try
                {
                    if (kvalue == null && selectqicountvalue == null)
                    {
                        //select
                        var finalstr = "";

                        lst = ps_Service.SelectProjSampleTablebyId(proj_id);
                        var kdata_col = "";
                        var delete_col = "";
                        var k_col_name = "";
                        var datas = "";
                        foreach (var item in lst)
                        {
                            ViewData["pro_tb"] = item.pro_tb.ToString();
                            newkvalue = item.minKvalue.ToString();
                            newselectqi = item.gen_qi_settingvalue;
                            if (newselectqi == "")
                            {
                                //如果參數禹資料庫都空直 return Step3
                                log.Info(" Step3_2 參數皆為空 退回 Step3  ");

                                return RedirectToAction("Step3", "ProjectStep", new { proj_id, project_name });
                            }
                            else
                            {     //"Table*5,7,請選擇,請選擇,6,6,請選擇*十歲區間,已上傳,,,50區間,100區間,"

                                //重新組合JSON
                                datas = item.data;
                                k_col_name = item.after_col_cht;
                                var k_col_array = k_col_name.Split(',');
                                ViewData["selectqigenvalue"] = newselectqi;
                                finalstr += item.pro_tb + "*" + item.gen_qi_settingvalue + "|";
                                ViewData["kvalue"] = item.minKvalue;
                                ViewData["r_value"] = item.r_value;
                                ViewData["T1"] = item.T1;
                                ViewData["T2"] = item.T2;
                                var qi_col = item.qi_col;

                                var colqiarr = qi_col.Split(',');
                                string qi_html = "<tr><td>{0}</td><td>{1}</td></tr>";
                                string qi_genstr = item.gen_qi_settingvalue;
                                var qi_genarr = qi_genstr.Split('*');
                                string[] level1value;
                                string[] level2value;
                                if (qi_genarr.Length > 2)
                                {
                                    level1value = qi_genarr[1].Split(',');
                                    level2value = qi_genarr[2].Split(',');
                                }
                                else
                                {
                                    level1value = qi_genarr[0].Split(',');
                                    level2value = qi_genarr[1].Split(',');
                                }


                                if (colqiarr.Length > 0)
                                {

                                    for (int i = 0; i < colqiarr.Length; i++)
                                    {
                                        //"5,7,請選擇,請選擇,6,6,請選擇*十歲區間,已上傳,,,50區間,100區間,"
                                        var data = colqiarr[i].Split('-');

                                        var qi_selectname = GetQIValueSelectName(level1value[i]);
                                        string name = "";
                                        string g_data = "";
                                        var qi_colname = colqiarr[i];
                                        name = data[0];
                                        k_col_name = k_col_name.Replace(name + ",", "");
                                        kdata_col += name + ",";
                                        if (qi_selectname == "請選擇")
                                        {
                                            //name = "不處理";
                                            g_data = "不處理";
                                        }
                                        else
                                        {
                                            //name = data[0];
                                            //  name = qi_selectname;
                                            if (level1value[i] == "6")
                                            {
                                                var updown = level2value[i].Split('#');
                                                g_data = " 下界 : " + updown[0] + "<br />" + " 數字區間 : " + updown[1] + "<br />" + " 上界 : " + updown[2];
                                            }
                                            else
                                            {
                                                g_data = qi_selectname + ":" + level2value[i];
                                            }
                                        }


                                        table_html += String.Format(qi_html, name, g_data);
                                    }

                                }

                            }
                            table_html += ",";
                            log.Info(" Step3_2 k_col_name after :  " + k_col_name);
                        }
                        table_html = table_html.Substring(0, table_html.Length - 1);
                        JArray kdataArr = JArray.Parse(datas);
                        var after_k_col = k_col_name.Split(',');
                        for (int b = 0; b < after_k_col.Length; b++)
                        {
                            foreach (JObject jobj in kdataArr)
                            {
                                jobj.Remove(after_k_col[b]);
                            }
                        }

                        string jsonString = kdataArr.ToString();
                        JArray col_data_setting_arr = JArray.Parse(jsonString);
                        log.Info("Step3_2 k_col_data : after new " + jsonString);
                        log.Info("Step3_2 k_col_data : after new " + col_data_setting_arr.ToString());
                        ViewData["new_sample_data"] = jsonString;

                        ViewData["selectqivalue"] = table_html;

                    }
                    else
                    {//"Table*5,7,請選擇,請選擇,6,6,請選擇*十歲區間,已上傳,,,50區間,100區間,"
                        ViewData["kvalue"] = kvalue;
                        //ViewData["selectqivalue"] = selectqicountvalue;
                        ViewData["selectqigenvalue"] = selectqicountvalue;
                        var selecttbqi = selectqicountvalue.Split('|');
                        var k_col_name = "";
                        var data_ori = "";
                        var kdata = "";
                        string qi_html = "<tr><td>{0}</td><td>{1}</td></tr>";
                        if (selecttbqi.Length > 0)
                        {

                            for (int i = 0; i < selecttbqi.Length; i++)
                            {
                                if (selecttbqi[i] != "")
                                {
                                    var tbqivalue_arr = selecttbqi[i].Split('*');
                                    lst = ps_Service.SelectProjSampleTable(proj_id, tbqivalue_arr[0]);
                                    string qi_colvalue = "";
                                    if (lst.Count() > 0)
                                    {
                                        foreach (var item in lst)
                                        {
                                            qi_colvalue = item.qi_col;
                                            k_col_name = item.after_col_cht;
                                            kdata = item.data;
                                            data_ori = item.data;
                                            var kl = kdata.Length;
                                        }
                                    }
                                    log.Info("Step3_2 k_col_name : before " + k_col_name);

                                    var colqiarr = qi_colvalue.Split(',');
                                    var level1value = tbqivalue_arr[1].Split(',');
                                    var level2value = tbqivalue_arr[2].Split(',');
                                    JArray kdataArr = JArray.Parse(kdata);
                                    var gen_data_string = "";
                                    // select table pid tbname
                                    if (colqiarr.Length > 0)
                                    {
                                        for (int x = 0; x < colqiarr.Length; x++)
                                        {
                                            //"5,7,請選擇,請選擇,6,6,請選擇*十歲區間,已上傳,,,50區間,100區間," Name,Gender,Education,IsRegistered,CarNo
                                            log.Info("gen 資料 :" + x + ": " + colqiarr[x]);
                                            //"5,7,請選擇,請選擇,6,6,請選擇*十歲區間,已上傳,,,50區間,100區間," Name,Gender,Education,IsRegistered,CarNo
                                            var teststr = "Name,Gender,Education,IsRegistered,CarNo";

                                            var data = colqiarr[x].Split('-');
                                            var qi_selectname = GetQIValueSelectName(level1value[x]);
                                            string name = "";
                                            string g_data = "";
                                            var qi_colname = colqiarr[x];
                                            name = data[0];
                                            if (x == colqiarr.Length - 1)
                                            {
                                                k_col_name = k_col_name.Replace(name, "");
                                            }
                                            else
                                            {
                                                k_col_name = k_col_name.Replace(name + ",", "");
                                            }

                                            if (qi_selectname == "請選擇" || qi_selectname == "不處理")
                                            {
                                                //name = "不處理";
                                                g_data = "不處理";
                                            }
                                            else
                                            {
                                                //name = data[0];
                                                //  name = qi_selectname;
                                                if (level1value[x] == "6")
                                                {
                                                    var updown = level2value[x].Split('#');
                                                    g_data = " 下界 : " + updown[0] + "<br />" + " 數字區間 : " + updown[1] + "<br />" + " 上界 : " + updown[2];
                                                }
                                                else
                                                {
                                                    g_data = qi_selectname + " : " + level2value[x];
                                                }

                                                var qi_level2 = GetQiLevel2(level1value[x], level2value[x]);
                                                //處理概化Sample
                                                var gen_setting = level1value[x].ToString();
                                                foreach (JObject jobj in kdataArr)
                                                {

                                                    log.Info("gen 資料 :" + selectqicountvalue);
                                                    //log.Info("gen 資料 :" + selectqicountvalue);
                                                    log.Info("gen 資料 1 :" + qi_colvalue);
                                                    log.Info("gen 資料 2:" + name);

                                                    switch (level1value[x])
                                                    {
                                                        case "1": //地址
                                                            //var newDate = "新竹縣竹東鎮燈會大道3段弄128號";
                                                            var newDate = jobj[name].ToString();
                                                            var newdata = genRandim.SettingQIAddress(newDate, level1value[x], qi_level2);
                                                            //var newdata = genRandim.SettingQIAddress(newDate, "2", level2value[x]);

                                                            log.Info("gen address new data :" + newdata);
                                                            jobj[name] = newdata;
                                                            break;
                                                        case "2": // 日期
                                                            DateTime dtDate;

                                                            var setDate = jobj[name].ToString();
                                                            if (DateTime.TryParse(setDate, out dtDate))
                                                            {
                                                                var setDate1 = "2023-03-14 05:20:30";
                                                                var connewDate = DateTime.Parse(setDate).ToString("yyyy-MM-dd");
                                                                var dateformate1 = connewDate.Substring(4, 1);

                                                                int index = connewDate.IndexOf(dateformate1, connewDate.IndexOf(dateformate1) + 1);

                                                                var dateformate2 = connewDate.Substring(index, 1);
                                                                if (dateformate1.Equals(dateformate2))
                                                                {
                                                                    if (dateformate1 != "-")
                                                                    {
                                                                        log.Info("格式-");
                                                                    }
                                                                    else if (dateformate1 != "/")
                                                                    {
                                                                        log.Info("格式/");
                                                                    }
                                                                }
                                                                else
                                                                {
                                                                    log.Info("格式不對");
                                                                    jobj[name] = "格式不對";
                                                                }
                                                                if (DateTime.TryParse(connewDate, out dtDate))
                                                                {
                                                                    log.Info("是日期");

                                                                    if (qi_level2 == "Y")
                                                                    {
                                                                        setDate = connewDate.Substring(0, 3);
                                                                    }
                                                                    else if (qi_level2 == "Mo")
                                                                    {
                                                                        setDate = connewDate.Substring(0, index);
                                                                    }
                                                                    else
                                                                    {
                                                                        //D
                                                                        setDate = connewDate.Substring(0, 9);
                                                                    }
                                                                }
                                                                else
                                                                {
                                                                    log.Info("錯誤日期");
                                                                }
                                                            }
                                                            else
                                                            {
                                                                log.Info("格式不對");
                                                                jobj[name] = "格式不對";
                                                            }
                                                            jobj[name] = setDate;
                                                            break;
                                                        case "3": //擷取字串
                                                            log.Info("擷取字串");
                                                            var str_sub = jobj[name].ToString();
                                                            string new_value = "";
                                                            if (string.IsNullOrEmpty(str_sub))
                                                            {
                                                                log.Info("isnull true");
                                                            }
                                                            else
                                                            {
                                                                log.Info("isnull false");
                                                                //有資料
                                                                log.Info(level2value[x]);
                                                                if (str_sub.Length >= int.Parse(level2value[x]))
                                                                {
                                                                    new_value = str_sub.Substring(0, int.Parse(level2value[x]));
                                                                }
                                                                else
                                                                {
                                                                    new_value = str_sub.Substring(0, str_sub.Length);

                                                                }
                                                                jobj[name] = new_value;
                                                            }
                                                            break;
                                                        case "4": //大區間
                                                            float StringToFloat;
                                                            bool level4 = float.TryParse(jobj[name].ToString(), out StringToFloat);
                                                            log.Info("level 4");
                                                            if (level4)
                                                            {
                                                                //是數字
                                                                log.Info("是數字");
                                                                var newdata_add = genRandim.SettingQINumberLevel(jobj[name].ToString(), level1value[x], qi_level2);
                                                                jobj[name] = newdata_add;
                                                            }
                                                            else
                                                            {
                                                                //不是數字
                                                                log.Info("非數字");
                                                            }
                                                            break;
                                                        case "5": //小區間
                                                            log.Info(level1value[x]);
                                                            log.Info(level2value[x]);
                                                            log.Info("level 5");
                                                            //確認是否為數字
                                                            float StringToFloatsmall;
                                                            bool IsFloat = float.TryParse(jobj[name].ToString(), out StringToFloatsmall);

                                                            if (IsFloat)
                                                            {
                                                                //是數字
                                                                log.Info("是數字");
                                                                var newdata_num = genRandim.SettingQINumberLevel(jobj[name].ToString(), level1value[x], qi_level2);
                                                                jobj[name] = newdata_num;
                                                            }
                                                            else
                                                            {
                                                                //不是數字
                                                                log.Info("非數字");
                                                            }
                                                            break;
                                                        case "6": //區間上下界
                                                            var updown = level2value[x].Split('#');
                                                            float updownlevel;
                                                            bool udlevel = float.TryParse(jobj[name].ToString(), out updownlevel);

                                                            if (udlevel)
                                                            {
                                                                //是數字
                                                                log.Info("是數字");
                                                                var newdata_Maxmin = genRandim.SettingQINumberMaxMin(jobj[name].ToString(), updown[1], int.Parse(updown[0]), int.Parse(updown[2]));
                                                                jobj[name] = newdata_Maxmin;
                                                            }
                                                            else
                                                            {
                                                                //不是數字
                                                                log.Info("非數字");
                                                            }
                                                            break;
                                                        default:
                                                            Console.WriteLine("Default case");
                                                            break;
                                                    }
                                                    var apiname = GetQIValueSelectName(level1value[x]);
                                                    var userRule = GetQiLevel2(level1value[x], level2value[x]);

                                                }
                                            }


                                            table_html += String.Format(qi_html, name, g_data);
                                        }


                                    }
                                    //log.Info("Login User :" + memberAcc + " Step3_2 k_col_name : after  " + k_col_name);
                                    JArray kdataArr1 = JArray.Parse(kdata);
                                    JArray dataOri_arr = JArray.Parse(data_ori);
                                    var after_k_col = k_col_name.Split(',');
                                    for (int b = 0; b < after_k_col.Length; b++)
                                    {
                                        foreach (JObject jobj in kdataArr1)
                                        {
                                            jobj.Remove(after_k_col[b]);
                                        }
                                        foreach (JObject jobjs in dataOri_arr)
                                        {
                                            jobjs.Remove(after_k_col[b]);
                                        }
                                    }

                                    string jsonString = kdataArr.ToString();
                                    JArray col_data_setting_arr = JArray.Parse(jsonString);
                                    string strdata = dataOri_arr.ToString();
                                    JArray data_setting_arr = JArray.Parse(strdata);

                                    //log.Info("Login User :" + memberAcc + " Step3_2 k_col_data : after new " + jsonString);
                                    //log.Info("Login User :" + memberAcc + " Step3_2 k_col_data : after new " + col_data_setting_arr.ToString());
                                    //var str_col_data_setting_arr = col_data_setting_arr.ToString().Substring(0, col_data_setting_arr.ToString().Length - 1);
                                    ViewData["new_sample_data"] = data_setting_arr.ToString(); //概化前資料
                                    ViewData["new_sample_data_after"] = col_data_setting_arr.ToString(); //概化前資料
                                }
                                table_html += ",";

                                //處理概化後
                            }
                        }
                        table_html = table_html.Substring(0, table_html.Length - 1);
                        ViewData["selectqivalue"] = table_html;
                    }

                    log.Info(" Step3_2 All Data :  " + table_html);

                }
                catch (Exception ex)
                {
                    Console.WriteLine("ex :" + ex.Message);
                    log.Error(" Step3_2 Exception :" + ex.Message);
                    // cht_name = User.FindFirst(ClaimTypes.Name)?.Value;
                    var logstr = "3_2 概化預覽錯誤: " + ex.Message;
                    log.Info(logstr);
                    //inslog = syslog_service.InsertSystemLog("1", "-1", "log", logstr);
                }
                return View(lst);
            }

        }

       // [Authorize]
        public IActionResult Step4(string proj_id, string project_name,string project_cht, string loginname, string returnurl)
        {
            ViewData["Project_cht"] = project_cht;
            ViewBag.LoginName = loginname;
            ViewData["ProjectId"] = proj_id;
            ViewData["ProjectName"] = project_name;
            ViewData["tbGenName"] = "";
            ViewData["job1"] = "";
            ViewData["kvalue"] = "";
            ViewData["job2"] = "";
            ViewData["job3"] = "";
            ViewData["job4"] = "";
            ViewData["job5"] = "";
            ViewData["ProjectStep"] = "";
            ViewData["returnurl"] = returnurl;
            ViewData["loginname"] = loginname;
            ViewData["tablename"] = "";
            log.Info("Step2 return url  :" + returnurl);
            log.Info("Step2 loginname  :" + loginname);
            // string prostatus = "";
            List<ProjectSampleDBData> lstST = null;
            try
            {
                var pstatus = psService.SelectProjectStatuis(int.Parse(proj_id));
                if (pstatus.Count > 0)
                {
                    foreach (var item in pstatus)
                    {
                        ViewData["ProjectStep"] = item.project_status;
                    }

                }
                //string colname = "";
                var lstfinalTB = ps_Service.SelectProjSampleTBKchek(proj_id, project_name);
                //List<Member> lstMember = new List<Member>();
                string selectname = _localizer.Text.select;
                lstfinalTB.Insert(0, new ProjectSampleDBData { ps_id = 0, finaltblName = selectname });
                lstfinalTB.Select(c => c.project_id == 7);
                ViewBag.listtb = lstfinalTB;

                string colqi = "";
                //  ViewData["tbData"] = "";
                // part 1 select sampletable
                lstST = ps_Service.SelectProjSampleTB(proj_id);
                if (lstST.Count > 0)
                {
                    foreach (var item in lstST)
                    {
                        ViewData["tbGenName"] = item.finaltblName;
                        colqi = item.qi_col;
                        ViewData["kvalue"] = item.minKvalue.ToString();
                        //  ViewData["colcht"] = "[" + item.after_col_cht + "]";
                    }
                }

            }
            catch (Exception ex)
            {
                log.Error("Step4 Exception :" + ex.Message);
            }
            return View(lstST);
        }

        //[Authorize]
        public IActionResult Step6(string proj_id, string project_name,string project_cht, string loginname, string returnurl)
        {
            ViewData["Project_cht"] = project_cht;
            ViewBag.LoginName = loginname;
            List<ProjectSampleDBData> lst = null;
            ViewData["returnurl"] = returnurl;
            ViewData["loginname"] = loginname;
            log.Info("Step2 return url  :" + returnurl);
            log.Info("Step2 loginname  :" + loginname);
            try
            {
                var prostatus = mydbhelper.UpdateProjectStauts(int.Parse(proj_id), 11, "報表查看");
                log.Info("Step6");
                var ifred = "N";
                ViewData["ProjectId"] = proj_id;
                ViewData["pro_tb"] = "";
                ViewData["ProjectName"] = project_name;
                ViewData["projectlist"] = "";
                ViewData["projectqi_list"] = "";
                ViewData["returnurl"] = returnurl;
                //var ranking_html = "<tr><td>{0}</td><td>{1}</td><td>{2}</td><td>{3}</td><td>{4}</td></tr>";
                //var ranking_html_first = "<tr><td>{0}</td><td>{1}</td><td>{2}</td></tr>";
                var ranking_html_first = "<tr><td>{0}</td><td>{1}</td><td>{2}</td><td>{3}</td><td>{4}</td></tr>";
                var ranking_html_sec = "<tr><td>{0}</td><td>{1}</td><td>{2}</td></tr>";
                var ranking_html_sec_red = "<tr><td>{0}</td><td>{1}</td><td class='warning_red'>{2}</td></tr>";
                //重新識別風險過高時警示
                //var ranking_html_red = "<tr><td>{0}</td><td>{1}</td><td class="warning_red">{2}</td><td>{3}</td><td>{4}</td></tr>";
                var current_setting_report1_html = "";
                string final_warning_html = "";
                string warning_html_table = "";
                string k_col_en = "";
                string k_col_cht = "";
                lst = ps_Service.SelectProjSampleTB(proj_id);
                string final_html = "";
                string sec_html = "";
                if (lst.Count > 0)
                {
                    foreach (var item in lst)
                    {
                        string pro_tb = "";
                        // string tablecount = "";
                        string supRate = "";
                        string warn_collist = "";
                        //string tablediscount = ""; 
                        if (item.pro_tb != null)
                        {
                            pro_tb = item.pro_tb;
                        }

                        if (item.supRate != null)
                            supRate = item.supRate.ToString();
                        if(item.k_risk!= null)
                        {
                            decimal maxt = 0;
                            decimal r_value = 0;
                            decimal k_risk = 0;
                            if(item.max_t!=null)
                            {
                                maxt = decimal.Round(decimal.Parse(item.max_t.ToString()), 2);
                            }

                            if (item.r_value != null)
                            {
                                r_value = decimal.Round(decimal.Parse(item.r_value.ToString()), 2);
                            }

                            if (item.k_risk != null)
                            {
                                k_risk = decimal.Round(decimal.Parse(item.k_risk.ToString()), 4);
                            }


                            if (decimal.Parse(item.k_risk.ToString()) < decimal.Parse(item.r_value.ToString()))
                            {
                                sec_html += String.Format(ranking_html_sec, maxt, r_value, k_risk);
                            }
                            else
                            {
                                ifred = "Y";
                                sec_html += String.Format(ranking_html_sec_red, maxt, r_value, k_risk);
                            }
                        }
                        k_col_cht = item.pro_col_cht;
                        k_col_en = item.pro_col_en;
                        final_html += String.Format(ranking_html_first, item.tableCount, item.tableDisCount, item.supCount, supRate, item.minKvalue.ToString());
                        log.Info("final_html : " + final_html);
                        //  ViewData["colcht"] = "[" + item.after_col_cht + "]";
                        var newselectqi = item.gen_qi_settingvalue;

                        var qi_col = item.qi_col;

                        var colqiarr = qi_col.Split(',');
                        // string qi_html = "<tr><td>{0}</td><td>{1}</td></tr>";
                        //var qi_html = "<tr><td>{0}</td><td>{1}</td><td>{2}</td><td>{3}</td></tr>";
                        var qi_html = "<tr><td>{0}</td><td>{1}</td><td>{2}</td>/tr>";
                        //Add 直接識別
                        var keylabel = item.tablekeycol;
                        if (keylabel != "")
                        {
                            var keyarr = keylabel.Split(',');
                            if (keyarr.Length > 0)
                            {
                                for (int z = 0; z < keyarr.Length; z++)
                                {
                                    current_setting_report1_html += String.Format(qi_html, keyarr[z], _localizer.Text.dir_id, "hash");
                                }
                            }
                        }
                        //current_setting_report1_html += String.Format(qi_html, name, name, colcheck, g_data);
                        string qi_genstr = item.gen_qi_settingvalue;
                        var qi_genarr = qi_genstr.Split('|');
                        var strlevel1value = "";
                        var strlevel2value = "";
                        if (qi_genarr.Length > 0)
                        {
                            for (int i = 0; i < qi_genarr.Length; i++)
                            {
                                if (qi_genarr[i] != "")
                                {
                                    var qi_gentbarr = qi_genarr[i].Split('*');
                                    strlevel1value = qi_gentbarr[1];
                                    strlevel2value = qi_gentbarr[2];
                                }
                            }
                        }
                        if (strlevel1value != "")
                        {
                            var level1value = strlevel1value.Split(',');
                            var level2value = strlevel2value.Split(',');


                            if (colqiarr.Length > 0)
                            {
                                for (int i = 0; i < colqiarr.Length; i++)
                                {
                                    //"5,7,請選擇,請選擇,6,6,請選擇*十歲區間,已上傳,,,50區間,100區間,"
                                    var data = colqiarr[i].Split('-');
                                    var qi_selectname = GetQIValueSelectName(level1value[i]);
                                    string name = "";
                                    string g_data = "";
                                    var qi_colname = colqiarr[i];
                                    name = data[0];
                                    string colcheck = "";
                                    switch (data[1])
                                    {
                                        case "1":
                                            colcheck = _localizer.Text.qi_id;
                                            break;
                                        case "2":
                                            colcheck = _localizer.Text.sensitive_id;
                                            break;
                                        case "3":
                                            colcheck = _localizer.Text.dir_id;
                                            break;
                                        case "4":
                                            colcheck = _localizer.Text.others;
                                            break;


                                    }
                                    if (qi_selectname == "請選擇" || qi_selectname == "不處理" || qi_selectname == "Select")
                                    {
                                        //name = "不處理";
                                        //g_data = _localizer.Text.unuse;
                                        g_data = "不處理";
                                    }
                                    else if (level1value[i] == "6")
                                    {
                                        var updown = level2value[i].Split('#');
                                        g_data = " 下界 : " + updown[0] + "<br />" + " 數字區間 : " + updown[1] + "<br />" + " 上界 : " + updown[2];
                                    }
                                    else
                                    {
                                        //name = data[0];
                                        //  name = qi_selectname;
                                        g_data = qi_selectname + ":" + level2value[i];
                                    }


                                    current_setting_report1_html += String.Format(qi_html, name, colcheck, g_data);
                                }


                                current_setting_report1_html += ",";
                            }
                        }
                        warn_collist = item.warning_col;
                        //string warning_colname = "";
                        //string warning_colvalue = "";


                        var warning_html = "<tr><td class='half_col'>{0}</td><td class='half_col text_right'>{1}<img src='/images/warning.png'></td></tr>";
                        if (warn_collist != null && warn_collist.Length > 0)
                        {

                            var warning_colarr = warn_collist.Split('*');
                            if (warning_colarr.Length > 1)
                            {
                                var warning_colname_arr = warning_colarr[0];
                                var warning_colvalue_arr = warning_colarr[1];
                                var warn_colname_arr = warning_colname_arr.Split(',');
                                var warn_colval_arr = warning_colvalue_arr.Split(',');
                                for (int i = 0; i < warn_colname_arr.Length; i++)
                                {
                                    warning_html_table += String.Format(warning_html, warn_colname_arr[i], warn_colval_arr[i]);
                                }

                            }
                            warning_html_table += ",";

                        }
                        else
                        {
                            warning_html_table += String.Format(warning_html, "No Column", "");
                            warning_html_table += ",";
                        }
                    }

                }
                if (warning_html_table.Length > 0)
                {
                    final_warning_html = warning_html_table.Substring(0, warning_html_table.Length - 1);
                    current_setting_report1_html = current_setting_report1_html.Substring(0, current_setting_report1_html.Length - 1);
                    ViewData["ifred"] = ifred;
                    ViewData["projectlist"] = final_html;
                    ViewData["projectlist_sec"] = sec_html;
                    ViewData["projectqitable"] = current_setting_report1_html;
                    ViewData["warningtablelist"] = final_warning_html;
                }
                else
                {
                    current_setting_report1_html = current_setting_report1_html.Substring(0, current_setting_report1_html.Length - 1);
                    final_warning_html = warning_html_table;
                    ViewData["ifred"] = ifred;
                    ViewData["projectlist"] = final_html;
                    ViewData["projectlist_sec"] = sec_html;
                    ViewData["projectqitable"] = current_setting_report1_html;
                    ViewData["warningtablelist"] = final_warning_html;
                }
                //ML Report
                ViewData["rp_tab_lst_1_1"] = "";
                ViewData["rp_tab_lst_1_2"] = "";

                ViewData["rp_tab_lst_1_count"] = "";

                ViewData["rp_tab_lst_2_1"] = "";
                ViewData["rp_tab_lst_2_2"] = "";

                ViewData["rp_tab_lst_2_count"] = "";
                ViewData["rp_tab_lst_3_1"] = "";
                ViewData["rp_tab_lst_3_2"] = "";

                ViewData["rp_tab_lst_3_count"] = "";
                string rb_tab1_data = "";
                string rb_tab2_data = "";
                string rb_tab3_data = "";
                ViewData["project_col_list"] = "";
                ViewData["RP_Count"] = "0";
                //string[] ml_model =["syn/raw", "raw/", ""];
                string tablist = "";
                //計算tab count
                //int pid = 123;
                int pid = int.Parse(proj_id);
                var utility_html = "<tr><td>{0}</td><td>{1}</td><td>{2}</td></tr>";
                var tab_fname = mydbhelper.SelectProUtilityResultCount(pid);
                if (tab_fname.Count > 0) //幾個tab
                {
                    ViewData["RP_Count"] = tab_fname.Count;
                    int z = 1;

                    foreach (var item in tab_fname)
                    {
                        var k_en_arr = k_col_en.Split(',');
                        var k_cht_arr = k_col_cht.Split(',');
                        var tar_col = item.target_col;
                        var new_target = "";
                        for (int b = 0; b < k_en_arr.Length; b++)
                        {
                            if (tar_col == k_en_arr[b].ToString())
                            {
                                new_target = k_cht_arr[b];
                            }
                        }
                        tablist += new_target + ",";
                        ViewData["pro_tb"] = item.deIdTbl;
                        var tab_model = mydbhelper.SelectdisResultModelCount(pid, item.target_col, item.deIdTbl);
                        if (tab_model.Count > 0)
                        {
                            int y = 1;
                            foreach (var itemdata in tab_model) //一個table 有3組Model
                            {
                                var lstutility = mydbhelper.SelectProUtilityResult(pid, item.target_col, itemdata.model);
                                if (lstutility.Count > 0)
                                {
                                    var utsr_result = "";

                                    List<mlresult_report> mlresult = new List<mlresult_report>();
                                    foreach (var items in lstutility) //同tab 會分三組 Model
                                    {
                                        utsr_result = items.MLresult;
                                        string newhtml = "";
                                        var decodeb64str = Encoding.UTF8.GetString(Convert.FromBase64String(utsr_result));
                                        decodeb64str = decodeb64str.Replace("\"", "");
                                        //JObject apidecode = JObject.Parse(utsr_result);
                                        JObject apidecode = JObject.Parse(decodeb64str);
                                        string xgbvalue = apidecode["XGBoost"].ToString();
                                        JObject apivalue_content = JObject.Parse(xgbvalue);
                                        string xg_ts = apivalue_content["Training Score"].ToString();
                                        string xg_vs = apivalue_content["Validation Score"].ToString();
                                        mlresult_report xgbvaluelst = new mlresult_report
                                        {
                                            model_name = "XGBoost",
                                            ts = xg_ts,
                                            vs = xg_vs
                                        };
                                        mlresult.Add(xgbvaluelst);
                                        //var utility_html = "<tr><td>{{model_name}}</td><td>{{ts}}</td><td>{{vs}}</td></tr>";
                                        newhtml += String.Format(utility_html, "XGBoost", xg_ts, xg_vs);
                                        string svmvalue = apidecode["SVM"].ToString();
                                        JObject svm_content = JObject.Parse(svmvalue);
                                        string svm_ts = svm_content["Training Score"].ToString();
                                        string svm_vs = svm_content["Validation Score"].ToString();
                                        mlresult_report svmvaluelst = new mlresult_report
                                        {
                                            model_name = "SVM",
                                            ts = svm_ts,
                                            vs = svm_vs
                                        };
                                        mlresult.Add(svmvaluelst);
                                        newhtml += String.Format(utility_html, "SVM", svm_ts, svm_vs);
                                        string rmvalue = apidecode["Random Forest"].ToString();
                                        JObject rm_content = JObject.Parse(rmvalue);
                                        string rm_ts = rm_content["Training Score"].ToString();
                                        string rm_vs = rm_content["Validation Score"].ToString();
                                        mlresult_report rmvaluelst = new mlresult_report
                                        {
                                            model_name = "Random Forest",
                                            ts = rm_ts,
                                            vs = rm_vs
                                        };
                                        mlresult.Add(rmvaluelst);
                                        newhtml += String.Format(utility_html, "Random Forest", rm_ts, rm_vs);
                                        string lsvalue = apidecode["Linear SVC"].ToString();
                                        JObject ls_content = JObject.Parse(lsvalue);
                                        string ls_ts = ls_content["Training Score"].ToString();
                                        string ls_vs = ls_content["Validation Score"].ToString();
                                        mlresult_report lsvaluelst = new mlresult_report
                                        {
                                            model_name = "Linear SVC",
                                            ts = ls_ts,
                                            vs = ls_vs
                                        };
                                        mlresult.Add(lsvaluelst);
                                        newhtml += String.Format(utility_html, "Linear SVC", ls_ts, ls_vs);

                                        string lrvalue = apidecode["Logistic Regression"].ToString();
                                        JObject lr_content = JObject.Parse(lrvalue);
                                        string lr_ts = lr_content["Training Score"].ToString();
                                        string lr_vs = lr_content["Validation Score"].ToString();
                                        mlresult_report lrvaluelst = new mlresult_report
                                        {
                                            model_name = "Logistic Regression",
                                            ts = lr_ts,
                                            vs = lr_vs
                                        };
                                        mlresult.Add(lrvaluelst);
                                        newhtml += String.Format(utility_html, "Logistic Regression", lr_ts, lr_vs);
                                        string mlresultInfo = JsonHelper.SerializeObject(mlresult);
                                        var strdataInfo = mlresultInfo;
                                        var jarrydataInfo = JArray.Parse(strdataInfo);
                                        if (z == 1)
                                        {
                                            if (y == 1)
                                            {
                                                ViewData["rp_tab_lst_1_1"] = newhtml;
                                            }
                                            else if (y == 2)
                                            {
                                                ViewData["rp_tab_lst_1_2"] = newhtml;
                                            }

                                        }
                                        else if (z == 2)
                                        {
                                            if (y == 1)
                                            {
                                                ViewData["rp_tab_lst_2_1"] = newhtml;
                                            }
                                            else if (y == 2)
                                            {
                                                ViewData["rp_tab_lst_2_2"] = newhtml;
                                            }

                                        }
                                        else //3
                                        {
                                            if (y == 1)
                                            {
                                                ViewData["rp_tab_lst_3_1"] = newhtml;
                                            }
                                            else if (y == 2)
                                            {
                                                ViewData["rp_tab_lst_3_2"] = newhtml;
                                            }

                                        }
                                        y++;
                                    }
                                }

                            }

                            z++;
                        }

                    }
                }
                if (tablist.Length > 2)
                {
                    //if (tablist.Substring(tablist.Length - 1, tablist.Length) == ",")
                    //{
                    tablist = tablist.Substring(0, tablist.Length - 1);
                    //}
                }

                ViewData["project_col_list"] = tablist;
                ViewData["risklist"] = "";
                ViewData["riskcount"] = "";
                //Get Risk Data
                var lstprotb = ps_Service.SelectProjSampleTB(proj_id);
                //               risk.list = [

                //       { risk_m: "隨機目標再識別風險（QI-based）", value: "0.11%"},
                //	{ risk_m: "單維敏感項目再識別風險（QI-based）", value: "0.11%"},
                //	{ risk_m: "多維敏感項目再識別風險（QI-based）", value: "0.11%"},
                //	{ risk_m: "多維敏感序列再識別風險", value: "0.00%"},
                //	{ risk_m: "單維敏感序列再識別風險", value: "0.00%"},
                //];
                //               var risk_html = "<tr><td class='half_col'>{{risk_m}}</td><td>{{value}}</td><td><div class='bar'><div class='percentage p1'></div></td></tr>";

                int rcount = 0;
                var risk_html = "<tr><td class='half_col'>{0}</td><td>{1}</td><td><div class='bar'><div class='{2}'></div></td></tr>";
                var new_risk_html = "";
                var final_risk_html = "";
                var muti_risk_html = "";
                if (lstprotb.Count > 0)
                {
                    rcount = lstprotb.Count;
                    foreach (var item in lstprotb)
                    {
                        ViewData["pro_tb"] = item.pro_tb;
                        //var lstrisk = mydbhelper.SelectProjRiskTable(18, "g_mac_adult_id_k_job1");
                        var lstrisk = mydbhelper.SelectProjRiskTable(int.Parse(proj_id), item.finaltblName);
                        if (lstrisk.Count > 0)
                        {
                            int x = 5;
                            string riskname = "";
                            string riskcss = "";
                            foreach (var items in lstrisk)
                            {
                                for (int i = 0; i < x; i++)
                                {
                                    var cssnm = "";
                                    new_risk_html = "";
                                    switch (i)
                                    {
                                        case 0:
                                            riskname = "隨機目標再識別風險（QI-based）";
                                            var r1 = Math.Round(items.r1, 5).ToString() + "%";
                                            cssnm = getriskcss(items.rs1);
                                            new_risk_html = String.Format(risk_html, riskname, r1, cssnm);
                                            break;
                                        case 1:
                                            riskname = "單維敏感項目再識別風險（QI-based）";
                                            var r2 = Math.Round(items.r2, 5).ToString() + "%";
                                            cssnm = getriskcss(items.rs2);
                                            new_risk_html = String.Format(risk_html, riskname, r2, cssnm);
                                            break;
                                        case 2:
                                            riskname = "多維敏感項目再識別風險（QI-based）";
                                            var r3 = Math.Round(items.r3, 5).ToString() + "%";
                                            cssnm = getriskcss(items.rs3);
                                            new_risk_html = String.Format(risk_html, riskname, r3, cssnm);
                                            break;
                                        case 3:
                                            riskname = "多維敏感序列再識別風險";
                                            var r4 = Math.Round(items.r4, 5).ToString() + "%";
                                            cssnm = getriskcss(items.rs4);
                                            new_risk_html = String.Format(risk_html, riskname, r4, cssnm);
                                            break;
                                        case 4:
                                            riskname = "單維敏感序列再識別風險";
                                            var r5 = Math.Round(items.r5, 5).ToString() + "%";
                                            cssnm = getriskcss(items.rs5);
                                            new_risk_html = String.Format(risk_html, riskname, r5, cssnm);
                                            break;
                                    }
                                    final_risk_html += new_risk_html;
                                }
                                x++;
                                muti_risk_html += final_risk_html + "|";
                            }
                        }
                    }
                }
                ViewData["risklist"] = muti_risk_html;
                ViewData["riskcount"] = rcount;
                return View(lst);
            }
            catch (Exception ex)
            {
                log.Info("Step6 Exception :" + ex.Message);
            }
            return View(lst);
        }
        private string getriskcss(string rs)
        {
            string cssnm = "";
            switch(rs)
            {
                case "1":
                    cssnm = "percentage p1";
                    break;
                case "2":
                    cssnm = "percentage p2";
                    break;
                case "3":
                    cssnm = "percentage p3";
                    break;
                case "4":
                    cssnm = "percentage p4";
                    break;
                case "5":
                    cssnm = "percentage p5";
                    break;
            }
            return cssnm;
        }
     //  [Authorize]
        public IActionResult Step7(string proj_id, string project_name,string project_cht, string loginname, string returnurl)
        {
            List<ProjectSampleDBData> lst = null;
            ViewBag.LoginName = loginname;
            ViewData["ProjectId"] = proj_id;
            ViewData["Project_cht"] = project_cht;
            ViewData["ProjectName"] = project_name;
            ViewData["returnurl"] = returnurl;
            ViewData["loginname"] = loginname;
            log.Info("Step2 return url  :" + returnurl);
            log.Info("Step2 loginname  :" + loginname);
            try
            {
                var prostatus = mydbhelper.UpdateProjectStauts(int.Parse(proj_id), 10, "資料匯出");
                log.Info("Step7");
                lst = ps_Service.SelectProjSampleTablebyId(proj_id);

            }
            catch (Exception ex)
            {
                log.Error("Step5 Exception :" + ex.Message);
            }
            return View(lst);
        }

        public IActionResult Step5_3(string proj_id, string project_name)
        {
            List<ProjectSampleDBData> lst = null;
            ViewData["ProjectId"] = proj_id;
            ViewData["ProjectName"] = project_name;

            try
            {
                lst = ps_Service.SelectProjSampleTablebyId(proj_id);

            }
            catch (Exception ex)
            {
                log.Error("Step5 Exception :" + ex.Message);
            }
            return View(lst);
        }

        public IActionResult Step5_4(string proj_id, string project_name, string project_cht)
        {
            ViewData["Project_cht"] = project_cht;
            List<ProjectSampleDBData> lst = null;

            try
            {
                var prostatus = mydbhelper.UpdateProjectStauts(int.Parse(proj_id), 11, "報表查看");
                log.Info("Step5_4");
                var ifred = "N";
                ViewData["ProjectId"] = proj_id;
                ViewData["pro_tb"] = "";
                ViewData["ProjectName"] = project_name;
                ViewData["projectlist"] = "";
                ViewData["projectqi_list"] = "";
                //var ranking_html = "<tr><td>{0}</td><td>{1}</td><td>{2}</td><td>{3}</td><td>{4}</td></tr>";
                var ranking_html_first = "<tr><td>{0}</td><td>{1}</td><td>{2}</td></tr>";
                var ranking_html_sec = "<tr><td>{0}</td><td>{1}</td><td>{2}</td></tr>";
                var ranking_html_sec_red = "<tr><td>{0}</td><td>{1}</td><td class='warning_red'>{2}</td></tr>";
                //重新識別風險過高時警示
                //var ranking_html_red = "<tr><td>{0}</td><td>{1}</td><td class="warning_red">{2}</td><td>{3}</td><td>{4}</td></tr>";
                var current_setting_report1_html = "";
                string final_warning_html = "";
                string warning_html_table = "";
                string k_col_en = "";
                string k_col_cht = "";
                lst = ps_Service.SelectProjSampleTB(proj_id);
                string final_html = "";
                string sec_html = "";
                if (lst.Count > 0)
                {
                    foreach (var item in lst)
                    {
                        k_col_cht = item.pro_col_cht;
                        k_col_en = item.pro_col_en;
                    }
                }
                //ML Report
                ViewData["rp_tab_lst_1_1"] = "";
                ViewData["rp_tab_lst_1_2"] = "";

                ViewData["rp_tab_lst_1_count"] = "";

                ViewData["rp_tab_lst_2_1"] = "";
                ViewData["rp_tab_lst_2_2"] = "";

                ViewData["rp_tab_lst_2_count"] = "";
                ViewData["rp_tab_lst_3_1"] = "";
                ViewData["rp_tab_lst_3_2"] = "";

                ViewData["rp_tab_lst_3_count"] = "";
                string rb_tab1_data = "";
                string rb_tab2_data = "";
                string rb_tab3_data = "";
                ViewData["project_col_list"] = "";
                ViewData["RP_Count"] = "0";
                //string[] ml_model =["syn/raw", "raw/", ""];
                string tablist = "";
                //計算tab count
                //int pid = 123;
                int pid = int.Parse(proj_id);
                var utility_html = "<tr><td>{0}</td><td>{1}</td><td>{2}</td></tr>";
                var tab_fname = mydbhelper.SelectProUtilityResultCount(pid);
                if (tab_fname.Count > 0) //幾個tab
                {
                    ViewData["RP_Count"] = tab_fname.Count;
                    int z = 1;

                    foreach (var item in tab_fname)
                    {
                        var k_en_arr = k_col_en.Split(',');
                        var k_cht_arr = k_col_cht.Split(',');
                        var tar_col = item.target_col;
                        var new_target = "";
                        for (int b = 0; b < k_en_arr.Length; b++)
                        {
                            if (tar_col == k_en_arr[b].ToString())
                            {
                                new_target = k_cht_arr[b];
                            }
                        }
                        tablist += new_target + ",";
                        ViewData["pro_tb"] = item.deIdTbl;
                        var tab_model = mydbhelper.SelectdisResultModelCount(pid, item.target_col, item.deIdTbl);
                        if (tab_model.Count > 0)
                        {
                            int y = 1;
                            foreach (var itemdata in tab_model) //一個table 有3組Model
                            {
                                var lstutility = mydbhelper.SelectProUtilityResult(pid, item.target_col, itemdata.model);
                                if (lstutility.Count > 0)
                                {
                                    var utsr_result = "";

                                    List<mlresult_report> mlresult = new List<mlresult_report>();
                                    foreach (var items in lstutility) //同tab 會分三組 Model
                                    {
                                        utsr_result = items.MLresult;
                                        string newhtml = "";
                                        var decodeb64str = Encoding.UTF8.GetString(Convert.FromBase64String(utsr_result));
                                        decodeb64str = decodeb64str.Replace("\"", "");
                                        //JObject apidecode = JObject.Parse(utsr_result);
                                        JObject apidecode = JObject.Parse(decodeb64str);
                                        string xgbvalue = apidecode["XGBoost"].ToString();
                                        JObject apivalue_content = JObject.Parse(xgbvalue);
                                        string xg_ts = apivalue_content["Training Score"].ToString();
                                        string xg_vs = apivalue_content["Validation Score"].ToString();
                                        mlresult_report xgbvaluelst = new mlresult_report
                                        {
                                            model_name = "XGBoost",
                                            ts = xg_ts,
                                            vs = xg_vs
                                        };
                                        mlresult.Add(xgbvaluelst);
                                        //var utility_html = "<tr><td>{{model_name}}</td><td>{{ts}}</td><td>{{vs}}</td></tr>";
                                        newhtml += String.Format(utility_html, "XGBoost", xg_ts, xg_vs);
                                        string svmvalue = apidecode["SVM"].ToString();
                                        JObject svm_content = JObject.Parse(svmvalue);
                                        string svm_ts = svm_content["Training Score"].ToString();
                                        string svm_vs = svm_content["Validation Score"].ToString();
                                        mlresult_report svmvaluelst = new mlresult_report
                                        {
                                            model_name = "SVM",
                                            ts = svm_ts,
                                            vs = svm_vs
                                        };
                                        mlresult.Add(svmvaluelst);
                                        newhtml += String.Format(utility_html, "SVM", svm_ts, svm_vs);
                                        string rmvalue = apidecode["Random Forest"].ToString();
                                        JObject rm_content = JObject.Parse(rmvalue);
                                        string rm_ts = rm_content["Training Score"].ToString();
                                        string rm_vs = rm_content["Validation Score"].ToString();
                                        mlresult_report rmvaluelst = new mlresult_report
                                        {
                                            model_name = "Random Forest",
                                            ts = rm_ts,
                                            vs = rm_vs
                                        };
                                        mlresult.Add(rmvaluelst);
                                        newhtml += String.Format(utility_html, "Random Forest", rm_ts, rm_vs);
                                        string lsvalue = apidecode["Linear SVC"].ToString();
                                        JObject ls_content = JObject.Parse(lsvalue);
                                        string ls_ts = ls_content["Training Score"].ToString();
                                        string ls_vs = ls_content["Validation Score"].ToString();
                                        mlresult_report lsvaluelst = new mlresult_report
                                        {
                                            model_name = "Linear SVC",
                                            ts = ls_ts,
                                            vs = ls_vs
                                        };
                                        mlresult.Add(lsvaluelst);
                                        newhtml += String.Format(utility_html, "Linear SVC", ls_ts, ls_vs);

                                        string lrvalue = apidecode["Logistic Regression"].ToString();
                                        JObject lr_content = JObject.Parse(lrvalue);
                                        string lr_ts = lr_content["Training Score"].ToString();
                                        string lr_vs = lr_content["Validation Score"].ToString();
                                        mlresult_report lrvaluelst = new mlresult_report
                                        {
                                            model_name = "Logistic Regression",
                                            ts = lr_ts,
                                            vs = lr_vs
                                        };
                                        mlresult.Add(lrvaluelst);
                                        newhtml += String.Format(utility_html, "Logistic Regression", lr_ts, lr_vs);
                                        string mlresultInfo = JsonHelper.SerializeObject(mlresult);
                                        var strdataInfo = mlresultInfo;
                                        var jarrydataInfo = JArray.Parse(strdataInfo);
                                        if (z == 1)
                                        {
                                            if (y == 1)
                                            {
                                                ViewData["rp_tab_lst_1_1"] = newhtml;
                                            }
                                            else if (y == 2)
                                            {
                                                ViewData["rp_tab_lst_1_2"] = newhtml;
                                            }

                                        }
                                        else if (z == 2)
                                        {
                                            if (y == 1)
                                            {
                                                ViewData["rp_tab_lst_2_1"] = newhtml;
                                            }
                                            else if (y == 2)
                                            {
                                                ViewData["rp_tab_lst_2_2"] = newhtml;
                                            }

                                        }
                                        else //3
                                        {
                                            if (y == 1)
                                            {
                                                ViewData["rp_tab_lst_3_1"] = newhtml;
                                            }
                                            else if (y == 2)
                                            {
                                                ViewData["rp_tab_lst_3_2"] = newhtml;
                                            }

                                        }
                                        y++;
                                    }
                                }

                            }

                            z++;
                        }

                    }
                }
                if (tablist.Length > 2)
                {
                    //if (tablist.Substring(tablist.Length - 1, tablist.Length) == ",")
                    //{
                    tablist = tablist.Substring(0, tablist.Length - 1);
                    //}
                }



                ViewData["project_col_list"] = tablist;
                ViewData["risklist"] = "";
                ViewData["riskcount"] = "";

                return View(lst);
            }
            catch (Exception ex)
            {
                log.Info("Step5_4 ML Exception :" + ex.Message);
            }
            return View(lst);
        }
        

        [HttpPost]
        public async Task<IActionResult> UploadFile(IFormFile file)
        {
            if (file == null || file.Length == 0)
                return Content("file not selected");

            var path = Path.Combine(
                        Directory.GetCurrentDirectory(), "wwwroot/upload",
                        file.GetFilename());

            using (var stream = new FileStream(path, FileMode.Create))
            {
                await file.CopyToAsync(stream);
            }

            return RedirectToAction("Files");
        }

        [HttpPost]
        public async Task<IActionResult> UploadFiles(List<IFormFile> files)
        {
            if (files == null || files.Count == 0)
                return Content("files not selected");

            foreach (var file in files)
            {
                var path = Path.Combine(
                        Directory.GetCurrentDirectory(), "wwwroot",
                        file.GetFilename());

                using (var stream = new FileStream(path, FileMode.Create))
                {
                    await file.CopyToAsync(stream);
                }
            }

            return RedirectToAction("Files");
        }


        private string GetQiLevel2(string selectvalue, string selectlevel2)
        {
            string getQiSelectName = "";
            string apilevel = "";
            switch (selectvalue)
            {
                case "請選擇":
                    getQiSelectName = "請選擇";
                    break;
                case "0":
                    getQiSelectName = "請選擇";
                    break;
                case "1":
                    getQiSelectName = "地址";
                    //["直轄市、縣、市", "鄉、鎮、縣轄市、區", "村、里", "大道、路、街", "段", "巷","衖","號"];	// 地址
                    switch (selectlevel2)
                    {
                        case "直轄市、縣、市":
                            apilevel = "1";
                            break;
                        case "鄉、鎮、縣轄市、區":
                            apilevel = "2";
                            break;
                        case "村、里":
                            apilevel = "3";
                            break;
                        case "鄰":
                            apilevel = "4";
                            break;
                        case "大道、路、街":
                            apilevel = "5";
                            break;
                        case "段":
                            apilevel = "6";
                            break;
                        case "巷":
                            apilevel = "7";
                            break;
                        case "弄":
                            apilevel = "8";
                            break;
                        //case "衖":
                        //    apilevel = "7";
                        //break;
                        case "號":
                            apilevel = "9";
                            break;
                    }
                    break;
                case "2":
                    getQiSelectName = "日期";
                    //["西元-YYYY", "西元-YYYY-MM", "西元-YYYY-MM-DD", "民國年", "民國年+月"]
                    switch (selectlevel2)
                    {
                        case "西元-YYYY":
                            apilevel = "Y";
                            break;
                        case "西元-YYYY-MM":
                            apilevel = "Mo";
                            break;
                        case "西元-YYYY-MM-DD":
                            apilevel = "D";
                            break;
                        case "民國年":
                            apilevel = "CY";
                            break;
                        case "民國年+月":
                            apilevel = "CMo";
                            break;
                    }
                    break;
                case "3":
                    getQiSelectName = "擷取字串";
                    //["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"];
                    switch (selectlevel2)
                    {
                        case "1":
                            apilevel = "0_1";
                            break;
                        case "2":
                            apilevel = "0_2";
                            break;
                        case "3":
                            apilevel = "0_3";
                            break;
                        case "4":
                            apilevel = "0_4";
                            break;
                        case "5":
                            apilevel = "0_5";
                            break;
                        case "6":
                            apilevel = "0_6";
                            break;
                        case "7":
                            apilevel = "0_7";
                            break;
                        case "8":
                            apilevel = "0_8";
                            break;
                        case "9":
                            apilevel = "0_9";
                            break;
                        case "10":
                            apilevel = "0_10";
                            break;
                    }
                    break;
                case "4":
                    getQiSelectName = "數字大區間";
                    // [ "十", "百", "千", "萬", "十萬", "百萬", "千萬", "億", "兆"];	/
                    switch (selectlevel2)
                    {
                        case "十":
                            apilevel = "10";
                            break;
                        case "百":
                            apilevel = "100";
                            break;
                        case "千":
                            apilevel = "1000";
                            break;
                        case "萬":
                            apilevel = "10000";
                            break;
                        case "十萬":
                            apilevel = "100000";
                            break;
                        case "百萬":
                            apilevel = "1000000";
                            break;
                        case "千萬":
                            apilevel = "10000000";
                            break;
                        case "億":
                            apilevel = "100000000";
                            break;
                        case "兆":
                            apilevel = "1000000000000";
                            break;
                    }
                    break;
                case "5":
                    getQiSelectName = "數字小區間";
                    apilevel = selectlevel2;
                    // ["三歲區間", "五歲區間", "十歲區間", "十五歲區間", "二十歲區間"]
                    break;
                case "6":
                    getQiSelectName = "數字區間含上下界";
                    //["50區間", "100區間", "500區間", "1000區間", "5,000區間", "10,000區間", "50,000區間", "100,000區間", "500, 000區間", "1,000,000區間", "5,000,000區間", "10,000,000區間", "50,000,000區間","100,000,000區間"]
                    var updown = selectlevel2.Replace('#', ',');
                    apilevel = updown;
                    break;
                case "7":
                    getQiSelectName = "";
                    break;
                    //case "8":
                    //    getQiSelectName = "Hash";
                    //    break;
                    //case "9":
                    //    getQiSelectName = "離群值處理";
                    //    break;
            }
            log.Info("概化設定內容第一層 :" + getQiSelectName);
            log.Info("概化設定內容第二層 :" + selectlevel2);
            log.Info("概化設定API內容第二層 :" + apilevel);

            return apilevel;
        }


        [HttpPost]
        public async Task<IActionResult> UploadFileViaModel(FileInputModel model)
        {
            if (model == null ||
                model.FileToUpload == null || model.FileToUpload.Length == 0)
                return Content("file not selected");

            var path = Path.Combine(
                        Directory.GetCurrentDirectory(), "wwwroot",
                        model.FileToUpload.GetFilename());

            using (var stream = new FileStream(path, FileMode.Create))
            {
                await model.FileToUpload.CopyToAsync(stream);
            }

            return RedirectToAction("Files");
        }
    }
}