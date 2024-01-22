using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using DeIdWeb.Infrastructure.Service;
using DeIdWeb.Models;
using Newtonsoft.Json;
using Microsoft.AspNetCore.Mvc;
using Newtonsoft.Json.Linq;
using System.IO;
using log4net;

using DeIdWeb.Filters;
using Resources;
using Microsoft.AspNetCore.Http;
using System.Web;
using Microsoft.AspNetCore.Authorization;
using System.Threading;
//using Microsoft.AspNetCore.Mvc.ViewFeatures;

namespace DeIdWeb.Controllers
{
    [TypeFilter(typeof(CultureFilter))]
    public class ProjectStepController : Controller
    {
        public HttpHelper httphelp = new HttpHelper();
        public MySqlDBHelper mydbhelper = new MySqlDBHelper();
        public ProjectStatus_Service psService = new ProjectStatus_Service();
        public ProjectSample_Service ps_Service = new ProjectSample_Service();
        //
        private ILog log = LogManager.GetLogger(Startup.repository.Name, typeof(ProjectStepController));

        private readonly ILocalizer _localizer;
        private readonly DpConnHelper _dpconn;

        public ProjectStepController(ILocalizer localizer, DpConnHelper dpconn)
        {
            _localizer = localizer;
            _dpconn = dpconn;
        }
       // [Authorize]
        public IActionResult Preview(string proj_id, string project_name, string stepstatus,string project_cht) //import
        {
            ViewData["Project_cht"] = project_cht;
            ViewData["ProjectName"] = project_name;
            ViewData["ProjectId"] = proj_id;
            ViewData["ProjectStep"] = stepstatus;
            ViewData["file"] ="";//"專案資料夾無資料";
            if (stepstatus == "1")
            {
                
            }
            var prostatus = mydbhelper.UpdateProjectStauts(int.Parse(proj_id), 1, "資料匯入");
            //var psresult = psService(int.Parse(proj_id), 1, "資料匯入");
            string sql = "select * from T_Project where project_id=" + proj_id + " and project_name='" + project_name + "'";
            try
            {
                var prolist = mydbhelper.SelectProject(sql);
                foreach (var item in prolist)
                {
                    ViewData["ProjectDesc"] = item.Project_desc;
                }

                //"{\"projName\": \"test_import_all\", \"projStep\": \"getServerFolder\", \"projID\": \"1\"}"

                createFolderAPI serverfolder = new createFolderAPI
                {
                    userID="1",
                    projID = proj_id,
                    projName = project_name,
                    
                    
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
                var apirestult = HttpHelper.PostUrl("getFolder_async", strapi);
                log.Info("getFolder_async return base64:" + apirestult);
                //"{\n  \"ERRMSG\": null, \n  \"STATE\": \"Fail\", \n  \"celeyId\": \"df428da1-1915-4a92-a958-5391a5e7535f\", \n  \"projStep\": \"get folder information\", \n  \"stateno\": null, \n  \"time_async\": \"0.57347202301\"\n}\n"
                //"{\n  \"PID\": 53, \n  \"celeyId\": \"ed7af7de-1f17-486e-b0f6-a5e19c163bfa\", \n  " +
                //    "\"fileNames\": \"adult.csv\", \n  \"projID\": \"2\", \n  \"projName\": \"adult\", " +
                //    "\n  \"projStep\": \"getfolder\", \n  \"time_async\": \"0.559223890305\", \n  \"userID\": \"1\"\n}\n"
                //var oldapiresult = "eyJzdGF0dXMiOiAtMSwgImZvbGRlcnMiOiAiIiwgImVyck1zZyI6ICJDYW5ub3QgZmluZCBhbnkgZmlsZXMgaW4gdGhpcyBwcm9qZWN0In0=";
                //var oldapiresult = "eyJwcm9qTmFtZSI6ICIyUURhdGFNYXJrZXREZUlkIiwgInByb2pTdGVwIjogImdlbiIsICJwcm9qSUQiOiAiMSIsICJtYWluSW5mbyI6IHsidGJsXzEiOiB7ImNvbEluZm8iOiB7ImNvbF8xIjogeyJjb2xOYW1lIjogImNfMjczN18xIiwgImFwaU5hbWUiOiAiZ2V0R2VuTnVtTGV2ZWwiLCAidXNlclJ1bGUiOiAiMTAifSwgImNvbF82IjogeyJjb2xOYW1lIjogImNfMjczN182IiwgImFwaU5hbWUiOiAiZ2V0R2VuVWRmIiwgInVzZXJSdWxlIjogIi9hcHAvYXBwL2RldnAvdWRmUnVsZS8ycWRhdGFtYXJrZXRkZWlkL3VkZm1hY3VpZF9hZHVsdF9pZC9tYXJpdGFsX3N0YXR1c19ydWxlLnR4dCJ9LCAiY29sXzExIjogeyJjb2xOYW1lIjogImNfMjczN18xMSIsICJhcGlOYW1lIjogImdldEdlbk51bUxldmVsIiwgInVzZXJSdWxlIjogIjUwIn0sICJjb2xfMTIiOiB7ImNvbE5hbWUiOiAiY18yNzM3XzEyIiwgImFwaU5hbWUiOiAiZ2V0R2VuTnVtTGV2ZWwiLCAidXNlclJ1bGUiOiAiMTAwIn0sICJjb2xfMTMiOiB7ImNvbE5hbWUiOiAiY18yNzM3XzEzIiwgImFwaU5hbWUiOiAiZ2V0R2VuTnVtSW50ZXJ2YWwiLCAidXNlclJ1bGUiOiAiMV8xMF81XjExXzIwXzE1XjIxXzEwMF8yNSJ9fSwgInRibE5hbWUiOiAidWRmTWFjVUlEX2FkdWx0X2lkIiwgImNvbF9lbiI6ICJjXzI3MzdfMCxjXzI3MzdfMSxjXzI3MzdfMixjXzI3MzdfMyxjXzI3MzdfNCxjXzI3MzdfNSxjXzI3MzdfNixjXzI3MzdfNyxjXzI3MzdfOCxjXzI3MzdfOSxjXzI3MzdfMTAsY18yNzM3XzExLGNfMjczN18xMixjXzI3MzdfMTMsY18yNzM3XzE0LGNfMjczN18xNSJ9fX0=";
                JObject apiresultJsobj = JObject.Parse(apirestult);
                //JObject apiresultJsobj = JObject.Parse(apirestult);
                string state = apiresultJsobj["STATE"].ToString();
                if (state == "FAIL")
                {
                    ViewData["file"] = "";
                    string errmsg = apiresultJsobj["ERRMSG"].ToString();
                    log.Error("Preview State Error :" + state);
                }
                else
                {
                    //增加判斷
                    string fileNames = apiresultJsobj["fileNames"].ToString();
                    ViewData["file"] = fileNames;
                }
                //var jsapiresults = Encoding.UTF8.GetString(Convert.FromBase64String(apibase641));
                //log.Info("Sync getFolder_async return JsonString :" + jsapiresults);

            }
            catch (Exception ex)
            {
                log.Error("Preview :" + ex.Message);
            }
            return View();
        }
     //   [Authorize]
        public IActionResult GanSync(string proj_id, string project_name, string project_cht, string loginname, string returnurl)
        {
            ViewData["ProjectId"] = proj_id;
            ViewData["ProjectName"] = project_name;
            ViewData["Project_Cht"] = project_cht;
            ViewData["returnurl"] = returnurl;
            ViewData["loginname"] = loginname;

            log.Info("returnurl returnurl " + returnurl);
            ViewBag.LoginName = loginname;
            List<ProjectSample5Data> lstST = null;
            ViewData["projectstatus"] = "";
            ViewData["ganselect_data"] = "";
            ViewData["returnurl"] = returnurl;
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
                lstST = ps_Service.SelectProjSample5TB(proj_id);
                log.Info("Step2 DataRow Count :" + lstST.Count());
                if (lstST.Count > 0)
                {
                    int x = 1;
                    foreach (var item in lstST)
                    {
                        //     JObject apidecode = JObject.Parse(item.data.ToString());
                        selectTable = item.file_name;
                        //ViewData["tbData"] = item.data.ToString();
                        string vdname = "tbData_" + x.ToString();
                        string colen = "colen_" + x.ToString();
                        ViewData["id_col"] = "";
                        ViewData["ganselect_data"] = item.select_data;
                        ViewData["filename"] = item.file_name;
                        ViewData["col_data"] = item.pro_col_cht;
                        ViewData["old_idcol"] = item.ID_Column.ToString();
                        var ob_col="";
                        if(item.ob_col != null)
                            ob_col = item.ob_col.ToString();
                        ViewData["ob_col_str"] = ob_col;
                        var id_col = item.ID_Column.ToString();
                        string new_id_col = "";
                        if (id_col != "")
                        {
                            var idcol_arr = id_col.Split(',');
                            if (idcol_arr.Length > 0)
                            {
                                for(int i=0;i <idcol_arr.Length;i++)
                                {
                                    if(idcol_arr[i]!="")
                                    {
                                        new_id_col += "「"+idcol_arr[i]+ "」"+",";
                                    }
                                }
                            }
                        }
                        if(new_id_col.Length >0)
                        {
                            new_id_col = new_id_col.Substring(0, new_id_col.Length - 1);
                        }

                        ViewData["id_col"] = new_id_col;
                        ViewData[vdname] = item.data.ToString();
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
                log.Error("GanSync Exception :" + ex.Message.ToString());
            }
            return View(lstST);
        }


        public IActionResult DpSync(string proj_id, string project_name, string project_cht, string loginname, string returnurl)
        {
            ViewData["ProjectId"] = proj_id;
            ViewData["ProjectName"] = project_name;
            ViewData["Project_Cht"] = project_cht;
            ViewData["returnurl"] = returnurl;
            ViewData["loginname"] = loginname;

            log.Info("returnurl returnurl " + returnurl);
            ViewBag.LoginName = loginname;
            List<ProjectSample5Data> lstST = null;
            ViewData["projectstatus"] = "";
            ViewData["ganselect_data"] = "";
            ViewData["returnurl"] = returnurl;
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
                lstST = ps_Service.SelectProjSample5TB(proj_id);
                log.Info("Step2 DataRow Count :" + lstST.Count());
                if (lstST.Count > 0)
                {
                    int x = 1;
                    foreach (var item in lstST)
                    {
                        //     JObject apidecode = JObject.Parse(item.data.ToString());
                        selectTable = item.file_name;
                        //ViewData["tbData"] = item.data.ToString();
                        string vdname = "tbData_" + x.ToString();
                        string colen = "colen_" + x.ToString();
                        ViewData["id_col"] = "";
                        ViewData["ganselect_data"] = item.select_data;
                        ViewData["filename"] = item.file_name;
                        ViewData["col_data"] = item.pro_col_cht;
                        ViewData["old_idcol"] = item.ID_Column.ToString();
                        var ob_col = "";
                        if (item.ob_col != null)
                            ob_col = item.ob_col.ToString();
                        ViewData["ob_col_str"] = ob_col;
                        var id_col = item.ID_Column.ToString();
                        string new_id_col = "";
                        if (id_col != "")
                        {
                            var idcol_arr = id_col.Split(',');
                            if (idcol_arr.Length > 0)
                            {
                                for (int i = 0; i < idcol_arr.Length; i++)
                                {
                                    if (idcol_arr[i] != "")
                                    {
                                        new_id_col += "「" + idcol_arr[i] + "」" + ",";
                                    }
                                }
                            }
                        }
                        if (new_id_col.Length > 0)
                        {
                            new_id_col = new_id_col.Substring(0, new_id_col.Length - 1);
                        }

                        ViewData["id_col"] = new_id_col;
                        ViewData[vdname] = item.data.ToString();
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
                log.Error("GanSync Exception :" + ex.Message.ToString());
            }
            return View(lstST);
        }

        //[Authorize]
        public IActionResult Dataassociation(string proj_id, string project_name, string project_cht, string loginname, string returnurl)
        {
            ViewData["ProjectId"] = proj_id;
            ViewData["ProjectName"] = project_name;
            ViewData["Project_Cht"] = project_cht;
            ViewData["ganselect_data"] = "";
            ViewData["ganselect_colname"] = "";
            List<ProjectSample5Data> lstST = null;
            ViewData["projectstatus"] = "";
            ViewData["returnurl"] = returnurl;
            ViewData["loginname"] = loginname;

            log.Info("returnurl returnurl " + returnurl);
            ViewBag.LoginName = loginname;
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
                lstST = ps_Service.SelectProjSample5TB(proj_id);
                log.Info("ML DataRow Count :" + lstST.Count());
                if (lstST.Count > 0)
                {
                    int x = 1;
                    foreach (var item in lstST)
                    {
                        //     JObject apidecode = JObject.Parse(item.data.ToString());
                        selectTable = item.file_name;
                        //ViewData["tbData"] = item.data.ToString();
                        string vdname = "tbData_" + x.ToString();
                        string colen = "colen_" + x.ToString();
                        ViewData["id_col"] = "";
                        ViewData["ganselect_data"] = item.select_data;
                        ViewData["ganselect_colname"] = item.select_colNames;
                        ViewData["filename"] = item.file_name;
                        ViewData["selectcol"] = item.selectcol;
                        ViewData["col_data"] = item.pro_col_cht;
                        ViewData["old_idcol"] = item.ID_Column.ToString();
                        ViewData["ob_col_str"] = item.ob_col.ToString();
                        var id_col = item.ID_Column.ToString();
                        string new_id_col = "";
                        if (id_col != "")
                        {
                            var idcol_arr = id_col.Split(',');
                            if (idcol_arr.Length > 0)
                            {
                                for (int i = 0; i < idcol_arr.Length; i++)
                                {
                                    if (idcol_arr[i] != "")
                                    {
                                        new_id_col += "「" + idcol_arr[i] + "」" + ",";
                                    }
                                }
                            }
                        }
                        if (new_id_col.Length > 0)
                        {
                            new_id_col = new_id_col.Substring(0, new_id_col.Length - 1);
                        }

                        ViewData["id_col"] = new_id_col;
                        ViewData[vdname] = item.data.ToString();
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
                log.Error("ML Exception :" + ex.Message.ToString());
            }
            return View(lstST);
        }


        //[Authorize]
        public IActionResult MLutility(string proj_id, string project_name, string project_cht, string loginname, string returnurl)
        {
            ViewData["ProjectId"] = proj_id;
            ViewData["ProjectName"] = project_name;
            ViewData["Project_Cht"] = project_cht;
            ViewData["ganselect_data"] = "";
            ViewData["ganselect_colname"] = "";
            List<ProjectSample5Data> lstST = null;
            ViewData["projectstatus"] = "";
            ViewData["returnurl"] = returnurl;
            ViewData["loginname"] = loginname;

            log.Info("returnurl returnurl " + returnurl);
            ViewBag.LoginName = loginname;
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
                lstST = ps_Service.SelectProjSample5TB(proj_id);
                log.Info("ML DataRow Count :" + lstST.Count());
                if (lstST.Count > 0)
                {
                    int x = 1;
                    foreach (var item in lstST)
                    {
                        //     JObject apidecode = JObject.Parse(item.data.ToString());
                        selectTable = item.file_name;
                        //ViewData["tbData"] = item.data.ToString();
                        string vdname = "tbData_" + x.ToString();
                        string colen = "colen_" + x.ToString();
                        ViewData["id_col"] = "";
                        ViewData["ganselect_data"] = item.select_data;
                        ViewData["ganselect_colname"] = item.select_colNames;
                        ViewData["filename"] = item.file_name;
                        ViewData["selectcol"] = item.selectcol;
                        ViewData["col_data"] = item.pro_col_cht;
                        ViewData["old_idcol"] = item.ID_Column.ToString();
                        ViewData["ob_col_str"] = item.ob_col.ToString();
                        var id_col = item.ID_Column.ToString();
                        string new_id_col = "";
                        if (id_col != "")
                        {
                            var idcol_arr = id_col.Split(',');
                            if (idcol_arr.Length > 0)
                            {
                                for (int i = 0; i < idcol_arr.Length; i++)
                                {
                                    if (idcol_arr[i] != "")
                                    {
                                        new_id_col += "「" + idcol_arr[i] + "」" + ",";
                                    }
                                }
                            }
                        }
                        if (new_id_col.Length > 0)
                        {
                            new_id_col = new_id_col.Substring(0, new_id_col.Length - 1);
                        }

                        ViewData["id_col"] = new_id_col;
                        ViewData[vdname] = item.data.ToString();
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
                log.Error("ML Exception :" + ex.Message.ToString());
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


      //  [Authorize]
        public IActionResult ExportData(string proj_id, string project_name, string project_cht, string loginname, string returnurl)
        {
            List<UtilityResult> lstmlResult = null;
            ViewData["ProjectId"] = proj_id;
            ViewData["ProjectName"] = project_name;
            ViewData["Project_Cht"] = project_cht;
            ViewData["select_csvdata"] = "";
            ViewData["returnurl"] = returnurl;
            ViewData["loginname"] = loginname;

            ViewBag.LoginName = loginname;
            string select_csvdata = "";
            try
            {
                var prostatus = mydbhelper.UpdateProjectStauts(int.Parse(proj_id), 7, "資料匯出");
                lstmlResult = ps_Service.SelectUtiltyResult(int.Parse(proj_id));
                if(lstmlResult.Count > 0)
                {
                    foreach(var item in lstmlResult)
                    {
                        select_csvdata += item.select_csv + ",";
                    }

                    if(select_csvdata.Length > 0)
                    {
                        select_csvdata = select_csvdata.Substring(0, select_csvdata.Length - 1);
                    }

                    ViewData["select_csvdata"] = select_csvdata;

                    return View(lstmlResult);
                }
                else
                {
                    return View(lstmlResult);
                }
            }
            catch (Exception ex)
            {
                log.Error("ExportData Exception :" + ex.Message);

            }
            return View();
        }
        [Authorize]
        public IActionResult GanSyncReport_old(string proj_id, string project_name, string project_cht)
        {
            List<ProjectSampleDBData> lst = null;
            try
            {
                log.Info("Step GanSyncReport");
                ViewData["Project_Cht"] = project_cht;
                ViewData["ProjectId"] = proj_id;
                ViewData["ProjectName"] = project_name;
                ViewData["rp_tab_lst_1_1"] = "" ;
                ViewData["rp_tab_lst_1_2"] = "" ;
                ViewData["rp_tab_lst_1_3"] = "" ;
                ViewData["rp_tab_lst_1_count"] = "" ;
                
                ViewData["rp_tab_lst_2_1"] = "" ;
                ViewData["rp_tab_lst_2_2"] = "" ;
                ViewData["rp_tab_lst_2_3"] = "" ;
                ViewData["rp_tab_lst_2_count"] = "";
                ViewData["rp_tab_lst_3_1"] = "" ;
                ViewData["rp_tab_lst_3_2"] = "" ;
                ViewData["rp_tab_lst_3_3"] = "" ;
                ViewData["rp_tab_lst_3_count"] = "";
                string rb_tab1_data = "";
                string rb_tab2_data = "";
                string rb_tab3_data = "";
                ViewData["project_col_list"] = "" ;
                ViewData["RP_Count"] = "0";
                //string[] ml_model =["syn/raw", "raw/", ""];
                string tablist = "";
                //計算tab count
                var utility_html = "<tr><td>{0}</td><td>{1}</td><td>{2}</td></tr>";
                var tab_fname = mydbhelper.SelectProUtilityResultCount(int.Parse(proj_id));
                if (tab_fname.Count > 0) //幾個tab
                {
                    ViewData["RP_Count"] = tab_fname.Count;
                    int z = 1;
                    foreach (var item in tab_fname)
                    {
                        
                        tablist += item.target_col + ",";
                        var tab_model = mydbhelper.SelectdisResultModelCount(int.Parse(proj_id), item.target_col);
                        if (tab_model.Count > 0)
                        {
                            int y = 1;
                            foreach (var itemdata in tab_model) //一個table 有3組Model
                            {
                                var lstutility = mydbhelper.SelectProUtilityResult(int.Parse(proj_id), item.target_col, itemdata.model);
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
                                            else
                                            {
                                                ViewData["rp_tab_lst_1_3"] = newhtml;

                                            }
                                        }
                                        else if(z==2)
                                        {
                                            if (y == 1)
                                            {
                                                ViewData["rp_tab_lst_2_1"] = newhtml;
                                            }
                                            else if (y == 2)
                                            {
                                                ViewData["rp_tab_lst_2_2"] = newhtml;
                                            }
                                            else
                                            {
                                                ViewData["rp_tab_lst_2_3"] = newhtml;

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
                                            else
                                            {
                                                ViewData["rp_tab_lst_3_3"] = newhtml;

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
                else
                {
                    //無資料
                    return View(lst);
                }

                if (tablist.Length > 2)
                {
                    //if (tablist.Substring(tablist.Length - 1, tablist.Length) == ",")
                    //{
                        tablist = tablist.Substring(0, tablist.Length - 1);
                    //}
                }

                ViewData["project_col_list"] = tablist;
                return View(lst);
            }
            catch(Exception ex)
            {
                log.Info("GanSyncReport Exception :" + ex.Message);
            }
            return View(lst);
        }


       // [Authorize]
        public async Task<IActionResult> DpSyncReport(string proj_id, string project_name, string project_cht, string loginname,string returnurl)
        {
            List<ProjectSampleDBData> lst = null;
            string raw_newhtml = "";

            ViewBag.LoginName = loginname;
            string syn_newhtml = "";
            string select_csvdata = "";
            ViewData["returnurl"] = returnurl;
            ViewData["loginname"] = loginname;
            log.Info("returnurl returnurl "+ returnurl);
            var ranking_html_first = "<tr><td>{0}</td><td>{1}</td><td>{2}</td>";
            string final_html = "";
            string download_path = "";
            try
            {
                var upstatuspr = mydbhelper.UpdateProjectStauts(int.Parse(proj_id),7, "查看報表'");
                Thread.Sleep(6000);
                //var apiName1 = "api/de-identification/proc/41650035-287e-4213-94e8-e3e79be1bb1d";  // 替換成實際的 API 名稱
                //                                                                                   //var apiName = "api/de-identification/488/job/"+dp_id.ToString();  // 替換成實際的 API 名稱
                //var result1 = await _dpconn.getasync(apiName1);
                //log.Info("Step DpSyncReport");
                //ViewData["Project_Cht"] = project_cht;
                ViewData["ProjectId"] = proj_id;
                ViewData["ProjectName"] = project_name;
                var lstST = ps_Service.SelectProjSample5TB(proj_id);
                log.Info("ML DataRow Count :" + lstST.Count());
                var pname = "";
                var fname = "";
                int task_id = 0;
                var selectcol_name = "";
                var selectcolvalue = "";
                int dp_id = 0;
                if (lstST.Count > 0)
                {
                    foreach (var item in lstST)
                    {
                        pname = item.project_name;
                        fname = item.file_name;
                        task_id = item.sectaskid;
                        selectcol_name = item.selectcol;
                        selectcolvalue = item.selectcolvalue;
                        dp_id = item.dp_id;
                    }
                }
                var requestData = new
                {
                    task_id = -1,
                    privacy_level = "3",
                    epsilon = 1
                };
                ViewData["fname"] = fname;
                var apiName = "api/de-identification/" + task_id.ToString() + "/job/"+dp_id.ToString();  // 替換成實際的 API 名稱
                //var apiName = "api/de-identification/488/job/"+dp_id.ToString();  // 替換成實際的 API 名稱
                var data_path = "static/test/" + fname;
                //var apiBody = new
                //{
                //    data_path = data_path,
                //    task_name = pname,
                //    selected_attrs = new
                //    {
                //        names = names_arr,
                //        types = tpyes_arr
                //    },
                //    opted_cluster = new[]
                //    {
                //            opted_cluster_arr
                //        },
                //    white_list = new string[0]
                //};

                var result = await _dpconn.getasync(apiName);
                var downpath = _dpconn.returndownload();
                log.Info("DpService Report return :" + result);
                if(result!="error")
                {
                    JObject apiresultJsobj = JObject.Parse(result);
                    // JObject apiresultJsobj = JObject.Parse(apirestult);
                    string statistics_err = apiresultJsobj["statistics_err"].ToString();
                    download_path= downpath+apiresultJsobj["synthetic_path"].ToString();
                    ViewData["download_path"] = download_path;
                    JObject revalue = JObject.Parse(statistics_err);
                    string stdvalue = revalue["values"].ToString();
                    string attrvalues = revalue["attrs"].ToString();
                    var col = revalue["attrs"];
                    log.Info("std "+ stdvalue);
                    log.Info("std "+ attrvalues);
                    JObject revalues = JObject.Parse(stdvalue);

                    string std = revalues["std"].ToString();
                    var x_std = revalues["std"];
                    var x_mean = revalues["mean"];
                    string mean = revalues["mean"].ToString();
                    log.Info("std " + col.Count());
                    log.Info("std " + mean);
                    for(int i=0; i<col.Count(); i++)
                    {
                        final_html += String.Format(ranking_html_first, col[i], x_mean[i], x_std[i]);

                    }

                    log.Info(final_html);
                }
                else
                {
                    var upstatusprrp = mydbhelper.UpdateProjectStauts(int.Parse(proj_id), 99, "差分隱私處理錯誤'");

                }
                //{ "dp_id":274,"statistics_err":{ "measures":["mean","std"],"values":{ "std":["0.43%","2.15%","0.76%"],"mean":["0.18%","0.23%","0.04%"]},"attrs":["Age","fnlwgt","hours_per_week"]},"proc_id":"ffd885f9-c9ed-4abe-bf9c-70a8dc25e575","privacy_level":3,"epsilon":1.0,"status":3,"exp_round":0,"min_freq":0.0,"synthetic_path":"task_499/sim_level_3.csv","log_path":"","start_time":"2023-12-15T03:26:01Z","end_time":"2023-12-15T03:26:03Z","task_id":499}
                ViewData["reportlist"] = final_html;
                var assstatus = mydbhelper.UpdateProjectdownload(int.Parse(proj_id), download_path);

            }
            catch (Exception ex)
            {
                log.Error("GanSyncReport Exception :" + ex.Message);
            }
            return View(lst);
        }
        // 格式化值的方法
        private string FormatValue(object value)
        {
            if (double.TryParse(value.ToString(), out double numericValue))
            {
                // 如果可以成功轉換為 double，判斷是否為整數
                if (numericValue % 1 == 0)
                {
                    return numericValue.ToString("0"); // 顯示整數
                }
                else
                {
                    return numericValue.ToString("0.###"); // 顯示到小數第三位
                }
            }
            else
            {
                return value.ToString(); // 不能轉換為 double，保持原樣
            }
        }

        public class RootObject
        {
            public Dictionary<string, int> value { get; set; }
        }
    }
}