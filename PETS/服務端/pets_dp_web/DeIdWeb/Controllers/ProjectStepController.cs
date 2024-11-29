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
using DeIdWeb.Infrastructure.Reposiotry;
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

        public GenSettingRandomData genRandim = new GenSettingRandomData();
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
            Thread.Sleep(7000);
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
                        ViewData["corr_col"] = item.corr_col;
                        if (item.choose_corr_col != null)
                        {
                            ViewData["choose_corr_col"] = item.choose_corr_col;
                        }
                        else
                        {
                            ViewData["choose_corr_col"] = "";
                        }
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


         //[Authorize]
        public IActionResult DataCheck(string proj_id, string project_name, string project_cht, string loginname, string returnurl)
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
                        ViewData["ganselect_data"] = item.data;
                        ViewData["ganselect_colname"] = item.select_colNames;
                        ViewData["filename"] = item.file_name;
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

        public class ColumnData
        {
            public string col { get; set; }
            public double mean { get; set; }
            public double std { get; set; }
        }
        // [Authorize]
        public IActionResult New_DpSyncReport(string proj_id, string project_name, string project_cht, string loginname, string returnurl)
        {
            List<ProjectSampleDBData> lst = null;
            string raw_newhtml = "";

            ViewBag.LoginName = loginname;
            string syn_newhtml = "";
            string select_csvdata = "";
            ViewData["returnurl"] = returnurl;
            ViewData["loginname"] = loginname;
            log.Info("returnurl returnurl " + returnurl);
            try
            {
                log.Info("Step GanSyncReport");
                ViewData["Project_Cht"] = project_cht;
                ViewData["ProjectId"] = proj_id;
                ViewData["ProjectName"] = project_name;
                ViewData["target_col"] = "";
                ViewData["raw_target_1"] = "";
                ViewData["raw_target_2"] = "";
                ViewData["raw_target_3"] = "";
                ViewData["raw_data"] = "";
                ViewData["raw_data_1"] = "";
                ViewData["raw_data_2"] = "";
                ViewData["raw_data_3"] = "";
                ViewData["syn_target_1"] = "";
                ViewData["syn_target_2"] = "";
                ViewData["syn_target_3"] = "";
                ViewData["syn_data"] = "";
                ViewData["syn_data_1"] = "";
                ViewData["syn_data_2"] = "";
                ViewData["syn_data_3"] = "";
                string rb_tab1_data = "";
                string rb_tab2_data = "";
                string rb_tab3_data = "";
                ViewData["project_col_list"] = "";
                ViewData["RP_Count"] = "0";
                //string[] ml_model =["syn/raw", "raw/", ""];
                string tablist = "";
                var ep = 0.0;
                ViewData["ep"] = ep;

                //計算tab count
                var utility_html = "<tr><td>{0}</td><td>{1}</td><td>{2}</td><td>{3}</td></tr>";
                var lstST = ps_Service.SelectProjSample5TB(proj_id);
                if (lstST.Count > 0)
                {
                    string psStatus = "";
                    foreach (var item in lstST)
                    {
                        ep = item.epsilon;
                    }

                    ViewData["ep"] = ep;
                }
                var tab_fname = mydbhelper.SelectProUtilityResultCount(int.Parse(proj_id));
                if (tab_fname.Count > 0) //幾個tab
                {
                    foreach (var item in tab_fname)
                    {
                        var str_target_col = item.target_col;
                        ViewData["target_col"] = str_target_col;

                        var lstutility = mydbhelper.SelectProUtilityResult(int.Parse(proj_id), item.target_col, "statistic");
                        var target_col_str = str_target_col.Split('*');
                        if (lstutility.Count > 0)
                        {
                            var utsr_result = "";
                            List<mlresult_report> mlresult = new List<mlresult_report>();
                            foreach (var items in lstutility) //同tab 會分三組 Model
                            {
                                utsr_result = items.MLresult;

                                var decodeb64str = Encoding.UTF8.GetString(Convert.FromBase64String(utsr_result));
                                decodeb64str = decodeb64str.Replace("\"", "");
                                JObject apidecode = JObject.Parse(decodeb64str);

                                string raw_data = apidecode["raw data"].ToString();
                                string syn_data = apidecode["syn. data"].ToString();
                                JObject raw_str = JObject.Parse(raw_data);
                                JObject syn_str = JObject.Parse(syn_data);
                                for (int i = 0; i < target_col_str.Count(); i++)
                                {
                                    var target_raw_data = raw_str[target_col_str[i]].ToString();
                                    var target_syn_data = syn_str[target_col_str[i]].ToString();
                                    JObject raw_col_attr = JObject.Parse(target_raw_data);
                                    JObject syn_col_attr = JObject.Parse(target_syn_data);
                                    var raw_type = raw_col_attr["type"].ToString();
                                    var syn_type = syn_col_attr["type"].ToString();
                                    var value_content = "";
                                    var raw_value_content = "";
                                    if (raw_type == "category")
                                    {
                                        var typevalue = "類別型";
                                        JObject raw_value_attr = JObject.Parse(raw_col_attr["value"].ToString());
                                        var value_attr = raw_value_attr.ToString();
                                        // 将 JSON 字符串解析为 Dictionary<string, int>
                                        Dictionary<string, int> valueDict = JsonConvert.DeserializeObject<Dictionary<string, int>>(value_attr);

                                        // 输出键和值
                                        foreach (var kvp in valueDict)
                                        {
                                            Console.WriteLine($"欄位內容 : {kvp.Key}, 類別數: {kvp.Value}");
                                            raw_value_content += $"{kvp.Key} : {kvp.Value}" + "筆" + "</br>";
                                        }
                                        //  raw_newhtml += String.Format(utility_html, target_col_str[i], typevalue, raw_value_content);

                                        JObject syn_value_attr = JObject.Parse(syn_col_attr["value"].ToString());
                                        var value_attr_syn = syn_value_attr.ToString();
                                        // 将 JSON 字符串解析为 Dictionary<string, int>
                                        Dictionary<string, int> syn_valueDict = JsonConvert.DeserializeObject<Dictionary<string, int>>(value_attr_syn);
                                        value_content = "";
                                        // 输出键和值
                                        foreach (var kvp in syn_valueDict)
                                        {
                                            Console.WriteLine($"欄位內容 : {kvp.Key}, 類別數: {kvp.Value}");
                                            value_content += $"{kvp.Key} : {kvp.Value}" + "筆" + "</br>";
                                        }
                                        raw_newhtml += String.Format(utility_html, target_col_str[i], typevalue, raw_value_content, value_content);
                                    }
                                    else
                                    {
                                        JObject raw_value_attr = JObject.Parse(raw_col_attr["value"].ToString());
                                        var value_attr = raw_value_attr.ToString();
                                        var typevalue = "數值型";
                                        // 将 JSON 字符串解析为 Dictionary<string, int>
                                        Dictionary<string, double> valueDict = JsonConvert.DeserializeObject<Dictionary<string, double>>(value_attr);

                                        // 输出键和值
                                        foreach (var kvp in valueDict)
                                        {
                                            Console.WriteLine($"欄位內容 : {kvp.Key}, 類別數: {kvp.Value.ToString()}");
                                            if (kvp.Key == "min")
                                            {
                                                raw_value_content += $"最小值 : {FormatValue(kvp.Value)}" + "</br>";
                                            }
                                            else if (kvp.Key == "max")
                                            {
                                                raw_value_content += $"最大值 : {FormatValue(kvp.Value)}" + "</br>";
                                            }
                                            else if (kvp.Key == "mean")
                                            {
                                                raw_value_content += $"平均數 : {FormatValue(kvp.Value)}" + "</br>";
                                            }
                                            else if (kvp.Key == "median")
                                            {
                                                raw_value_content += $"中位數 : {FormatValue(kvp.Value)}" + "</br>";
                                            }
                                            else
                                            {
                                                raw_value_content += $"標準差 : {FormatValue(kvp.Value)}" + "</br>";
                                            }


                                        }
                                     //   raw_newhtml += String.Format(utility_html, target_col_str[i], typevalue, value_content);

                                        JObject syn_value_attr = JObject.Parse(syn_col_attr["value"].ToString());
                                        var value_attr_syn = syn_value_attr.ToString();
                                        // 将 JSON 字符串解析为 Dictionary<string, int>
                                        Dictionary<string, double> syn_valueDict = JsonConvert.DeserializeObject<Dictionary<string, double>>(value_attr_syn);
                                        value_content = "";
                                        // 输出键和值
                                        foreach (var kvp in syn_valueDict)
                                        {
                                            Console.WriteLine($"欄位內容 : {kvp.Key}, 類別數: {kvp.Value}");
                                            Console.WriteLine($"欄位內容 : {kvp.Key}, 類別數: {kvp.Value}");
                                            if (kvp.Key == "min")
                                            {
                                                value_content += $"最小值 : {FormatValue(kvp.Value)}" + "</br>";
                                            }
                                            else if (kvp.Key == "max")
                                            {
                                                value_content += $"最大值 : {FormatValue(kvp.Value)}" + "</br>";
                                            }
                                            else if (kvp.Key == "mean")
                                            {
                                                value_content += $"平均數 : {FormatValue(kvp.Value)}" + "</br>";
                                            }
                                            else if (kvp.Key == "median")
                                            {
                                                value_content += $"中位數 : {FormatValue(kvp.Value)}" + "</br>";
                                            }
                                            else
                                            {
                                                value_content += $"標準差 : {FormatValue(kvp.Value)}" + "</br>";
                                            }

                                        }
                                        //  syn_newhtml += String.Format(utility_html, target_col_str[i], typevalue, value_content);
                                        raw_newhtml += String.Format(utility_html, target_col_str[i], typevalue, raw_value_content, value_content);

                                    }


                                }
                            }
                        }
                    }
                }
                else
                {
                    //無資料
                    return View(lst);
                }
                ViewData["syn_data"] = syn_newhtml;
                ViewData["raw_data"] = raw_newhtml;
                if (tablist.Length > 2)
                {
                    //if (tablist.Substring(tablist.Length - 1, tablist.Length) == ",")
                    //{
                    tablist = tablist.Substring(0, tablist.Length - 1);
                    //}
                }

                ViewData["project_col_list"] = tablist;

                //export
                var lstmlResult = ps_Service.SelectUtiltyResult(int.Parse(proj_id));
                if (lstmlResult.Count > 0)
                {
                    foreach (var item in lstmlResult)
                    {
                        select_csvdata += item.select_csv + ",";
                    }

                    if (select_csvdata.Length > 0)
                    {
                        select_csvdata = select_csvdata.Substring(0, select_csvdata.Length - 1);
                    }

                    ViewData["select_csvdata"] = select_csvdata;


                }

                return View(lst);
            }
            catch (Exception ex)
            {
                log.Error("GanSyncReport Exception :" + ex.Message);
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
                var dp_report_data = "";
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
                        dp_report_data = item.dp_report_data;
                    }
                }

                List<ColumnData> columnDataList = JsonConvert.DeserializeObject<List<ColumnData>>(dp_report_data);

                foreach (ColumnData columnData in columnDataList)
                {
                    final_html += String.Format(ranking_html_first, columnData.col, columnData.mean, columnData.std);
   
                }
                ViewData["reportlist"] = final_html;
                //var requestData = new
                //{
                //    task_id = -1,
                //    privacy_level = "3",
                //    epsilon = 1
                //};
                //ViewData["fname"] = fname;
                //var apiName = "api/de-identification/" + task_id.ToString() + "/job/"+dp_id.ToString();  // 替換成實際的 API 名稱
                ////var apiName = "api/de-identification/488/job/"+dp_id.ToString();  // 替換成實際的 API 名稱
                //var data_path = "static/test/" + fname;
                ////var apiBody = new
                ////{
                ////    data_path = data_path,
                ////    task_name = pname,
                ////    selected_attrs = new
                ////    {
                ////        names = names_arr,
                ////        types = tpyes_arr
                ////    },
                ////    opted_cluster = new[]
                ////    {
                ////            opted_cluster_arr
                ////        },
                ////    white_list = new string[0]
                ////};

                //var result = await _dpconn.getasync(apiName);
                //var downpath = _dpconn.returndownload();
                //log.Info("DpService Report return :" + result);
                //if(result!="error")
                //{
                //    JObject apiresultJsobj = JObject.Parse(result);
                //    // JObject apiresultJsobj = JObject.Parse(apirestult);
                //    string statistics_err = apiresultJsobj["statistics_err"].ToString();
                //    download_path= downpath+apiresultJsobj["synthetic_path"].ToString();
                //    ViewData["download_path"] = download_path;
                //    JObject revalue = JObject.Parse(statistics_err);
                //    string stdvalue = revalue["values"].ToString();
                //    string attrvalues = revalue["attrs"].ToString();
                //    var col = revalue["attrs"];
                //    log.Info("std "+ stdvalue);
                //    log.Info("std "+ attrvalues);
                //    JObject revalues = JObject.Parse(stdvalue);

                //    string std = revalues["std"].ToString();
                //    var x_std = revalues["std"];
                //    var x_mean = revalues["mean"];
                //    string mean = revalues["mean"].ToString();
                //    log.Info("std " + col.Count());
                //    log.Info("std " + mean);
                //    for(int i=0; i<col.Count(); i++)
                //    {
                //       // final_html += String.Format(ranking_html_first, col[i], x_mean[i], x_std[i]);

                //    }
                //    final_html += String.Format(ranking_html_first, "age_sys_coupon_c_new", "32.437", "10.435");
                //    final_html += String.Format(ranking_html_first, "income_sys_coupon_c_new", "1528697.571", "975395.248");

                //    log.Info(final_html);
                //}
                //else
                //{
                //    final_html += String.Format(ranking_html_first, "age_sys_coupon_c_new", "32.437", "10.435");
                //    final_html += String.Format(ranking_html_first, "income_sys_coupon_c_new", "1528697.571", "975395.248"); //// var upstatusprrp = mydbhelper.UpdateProjectStauts(int.Parse(proj_id), 99, "差分隱私處理錯誤'");

                //}
                ////{ "dp_id":274,"statistics_err":{ "measures":["mean","std"],"values":{ "std":["0.43%","2.15%","0.76%"],"mean":["0.18%","0.23%","0.04%"]},"attrs":["Age","fnlwgt","hours_per_week"]},"proc_id":"ffd885f9-c9ed-4abe-bf9c-70a8dc25e575","privacy_level":3,"epsilon":1.0,"status":3,"exp_round":0,"min_freq":0.0,"synthetic_path":"task_499/sim_level_3.csv","log_path":"","start_time":"2023-12-15T03:26:01Z","end_time":"2023-12-15T03:26:03Z","task_id":499}
                //ViewData["reportlist"] = final_html;
                //var assstatus = mydbhelper.UpdateProjectdownload(int.Parse(proj_id), download_path);

            }
            catch (Exception ex)
            {
                //final_html += String.Format(ranking_html_first, "age_sys_coupon_c_new", "32.437", "10.435");
                //final_html += String.Format(ranking_html_first, "income_sys_coupon_c_new", "1528697.571", "975395.248"); //final_html += String.Format(ranking_html_first, "hours-per-week_sys_w1_adult_test_enc", "40.67", "12.17");
                ////final_html += String.Format(ranking_html_first, "capital-gain_sys_w1_adult_test_enc", "1092.28", "7617.54");
                ////final_html += String.Format(ranking_html_first, "age_sys_w1_adult_test_enc", "36.71", "12.91");
                //  final_html += String.Format(ranking_html_first, "capital-gain_sys_w1_adult_test_enc", "1.30%", "0.45%");
                ViewData["reportlist"] = final_html;
                log.Error("GanSyncReport Exception :" + ex.Message);
            }
            return View(lst);
        }

        // [Authorize]
        public IActionResult Step3(string proj_id, string project_name, string project_cht, string loginname, string returnurl)
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
                        if (mink == "0")
                        {
                            mink = "3";
                        }
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

        /// <summary>
        /// 
        /// </summary>
        /// <param name="proj_id"></param>
        /// <param name="project_name"></param>
        /// <param name="kvalue"></param>
        /// <param name="base64selectqi"></param>
        /// <param name="project_cht"></param>
        /// <param name="loginname"></param>
        /// <param name="returnurl"></param>
        /// <returns></returns>
        public IActionResult Step3_2(string proj_id, string project_name, string kvalue, string base64selectqi, string project_cht, string loginname, string returnurl)
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

                        lst = ps_Service.SelectProjSample5TablebyId(proj_id);
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
                                k_col_name = item.select_colNames;
                                var k_col_array = k_col_name.Split(',');
                                ViewData["selectqigenvalue"] = newselectqi;
                                finalstr += item.pro_tb + "*" + item.gen_qi_settingvalue + "|";

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
                                    lst = ps_Service.SelectProjSample5Table(proj_id, tbqivalue_arr[0]);
                                    string qi_colvalue = "";
                                    if (lst.Count() > 0)
                                    {
                                        foreach (var item in lst)
                                        {
                                            qi_colvalue = item.qi_col;
                                            k_col_name = item.select_colNames;
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