using System;
using System.Collections.Generic;
using System.Linq;
using System.Net;
using System.Net.Http;
using System.Text;
using System.Threading;
using System.Threading.Tasks;
using System.Xml.Linq;
using DeIdWeb.Filters;
using DeIdWeb.Infrastructure.Reposiotry;
using DeIdWeb.Infrastructure.Service;
using DeIdWeb.Models;
using Google.Protobuf.Collections;
using log4net;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Localization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Extensions.Configuration;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;
using Resources;

namespace DeIdWeb.Controllers
{
    [TypeFilter(typeof(CultureFilter))]
    [Produces("application/json")]
    [Route("api/WebAPI")]

    public class WebAPIController : Controller
    {
        public ProjectStatus_Service psService = new ProjectStatus_Service();
        public MySqlDBHelper mydbhelper = new MySqlDBHelper();

        public ProjectStatus_Service projService = new ProjectStatus_Service();
        public ProjectSample_Service proj_Service = new ProjectSample_Service();
        public HttpHelper httphelper = new HttpHelper();
        public GetGenJsonRep genJsonRp = new GetGenJsonRep();
        private ILog log = LogManager.GetLogger(Startup.repository.Name, typeof(WebAPIController));
        private readonly ILocalizer _localizer;
        //DpConnHelper dpconn = new DpConnHelper();
        private readonly DpConnHelper _dpconn;

        private readonly IConfiguration _configuration;
        public WebAPIController(ILocalizer localizer, IConfiguration configuration, DpConnHelper dpconn)
        {
            _localizer = localizer;
            _configuration = configuration;
            _dpconn = dpconn;
        }


        /// <summary>
        /// 
        /// </summary>
        /// <param name="pid"></param>
        /// <param name="pname"></param>
        /// <param name="selectqivalue"></param>
        /// <param name="k_value"></param>
        /// <param name="tablename"></param>
        /// <returns></returns>
        [HttpGet("Generalizationasync")]
        public async Task<bool> Generalizationasync(string pid, string pname, string selectqivalue, string k_value, string tablename)
        {

            bool isGen = false;
            //bool isUpdate = false;
            log.Info("Generalizationasync 概化 WebAPI");
            log.Info("pid :" + pid);
            log.Info("pname :" + pname);
            log.Info("selectqivalue :" + selectqivalue);
            log.Info("k_value :" + k_value);
            //log.Info("r_value :" + r_value);
            //log.Info("t1_value :" + t1);
            //log.Info("t2_value :" + t2);
            log.Info("tablename :" + tablename);
            try
            {
                var tbarray = tablename.Split(',');
                string col_en = "";
                string col_cht = "";
                string projStep = "gen";
                string qi_value = "";
                // string tblName = "";
                string tbl = "tbl_";
                string tablelst = "";
                string genJson = "";
                for (int i = 0; i < tbarray.Length; i++)
                {
                    //select table 過濾 

                    var lstSampleTB = proj_Service.SelectProjSample5Table(pid, tbarray[i].ToString());
                    if (lstSampleTB == null)
                    {
                        return false;
                    }

                    tablelst = tbl + (i + 1).ToString();
                    if (lstSampleTB.Count > 0)
                    {
                        foreach (var item in lstSampleTB)
                        {
                            col_en = item.select_colNames;
                            col_cht = item.select_colNames;
                            qi_value = item.qi_col;
                        }
                    }

                    //判斷有無概化

                    var col_cht_array = col_cht.Split(',');
                    var col_qi_array = qi_value.Split(',');
                    var col_gentb_arr = selectqivalue.Split('|');
                    bool isgen = false;
                    for (int c = 0; c < col_gentb_arr.Length; c++)
                    {
                        if (col_gentb_arr[c] != "")
                        {
                            var col_gen_array = col_gentb_arr[c].Split('*');
                            var tbnm = col_gen_array[0];
                            var col_gen_level1 = col_gen_array[1];
                            var col_gen_level2 = col_gen_array[2];

                            log.Info("tbname :" + tbnm);

                            var gen_level1 = col_gen_level1.Split(',');
                            var gen_level2 = col_gen_level2.Split(',');


                            for (int j = 0; j < col_cht_array.Length; j++)
                            {   //"5,7,請選擇,請選擇,6,6,請選擇*十歲區間,已上傳,,,50區間,100區間,"
                                for (int x = 0; x < col_qi_array.Length; x++)
                                {
                                    var qi_item = col_qi_array[x].Split(',');
                                    var qi_item_array = qi_item[0].Split('-');
                                    if (col_cht_array[j] == qi_item_array[0])
                                    {
                                        if (gen_level1[x] != "0" && gen_level1[x] != "7")
                                        {
                                            isgen = true;
                                        }
                                    }
                                }
                            }
                        }
                    }

                    if (isgen)
                    {
                        genJson += genJsonRp.GetGenJsonAPI(pid, projStep, pname, col_en, col_cht, tablelst, tbarray[i].ToString(), qi_value, selectqivalue) + ",";
                        //var col_gentb_arr = selectqivalue.Split('|');
                        for (int b = 0; b < col_gentb_arr.Length; b++)
                        {
                            if (col_gentb_arr[b] != "")
                            {
                                var col_gen_array = col_gentb_arr[b].Split('*');
                                var tbnm = col_gen_array[0];
                                var col_gen_level1 = col_gen_array[1];
                                var col_gen_level2 = col_gen_array[2];
                                if (tbnm == tbarray[i])
                                {
                                    //var updatestresult = proj_Service.UpdateProjectSampleTableQI(pid, k_value, col_gentb_arr[b], tbarray[i],r_value,t1,t2);
                                    var updatestresult = proj_Service.UpdateProjectSampleTableQI(pid, "0", col_gentb_arr[b], tbarray[i]);
                                }
                            }
                        }

                        //接概化API
                        project_gen_api gensyncapi = new project_gen_api
                        {
                            project_id = int.Parse(pid),
                            privacy_type = "dp"
                        };

                        string strgenapi = JsonHelper.SerializeObject(gensyncapi);
                        log.Info("genData_async :" + strgenapi);
                        //  string serverfolderstr = JsonHelper.SerializeObject(serverfolder);
                        //  string jsondic = JsonHelper.SerializeObject(strgenapi);
                        //var apirestult = HttpHelper.PostUrl_pedsa("projects/genintegration_async", strgenapi);
                        var apirestult = await httphelper.PedsaPostUrl_async("projects/genintegration_async", int.Parse(pid), "dp");
                        //var apirestult = await httphelper.PostUrl_async("projects/genintegration_async", strgenapi);
                        JObject json = JObject.Parse(apirestult);

                        // 取得 status 值
                        string status = json["status"]?.ToString();

                        Console.WriteLine($"Status: {status}");
                        if (status == "accepted")
                        {
                            var prostatus = mydbhelper.UpdateProjectStauts(int.Parse(pid), 4, "概化與資料生成設定中....");
                            if (prostatus)
                            {
                                isGen = true;
                            }
                        }

                    }
                    else
                    {
                        //gan
                        //SendGanSyncService(pid, pname, ob_col, string selectcol, string keyName, string fname, string col_data);
                        var lstST = proj_Service.SelectProjSample5TB(pid);
                        var ob_col = "";
                        var selectcol = "";
                        var keyName = "";
                        var fname = "";
                        var col_data = "";
                        if (lstST.Count > 0)
                        {
                            int x = 1;
                            foreach (var item in lstST)
                            {
                                ob_col = item.ob_col;
                                selectcol = item.select_colNames;
                                keyName = item.ID_Column;
                                fname = item.file_name;
                                col_data = item.select_colNames;
                            }

                            var isGan = await SendDpService(pid, pname, ob_col, selectcol, keyName, fname, col_data);
                            if (isGan)
                                isGen = true;
                        }
                    }
                }

            }
            catch (Exception ex)
            {
                string errormsg = ex.Message;
                log.Error("Web API Generalizationasync Exception : " + errormsg);

            }
            return isGen;
        }



        /// <summary>
        /// 
        /// </summary>
        /// <param name="pid"></param>
        /// <param name="pname"></param>
        /// <param name="ob_col"></param>
        /// <param name="selectcol"></param>
        /// <param name="keyName"></param>
        /// <param name="fname"></param>
        /// <param name="col_data"></param>
        /// <returns></returns>
        [HttpGet("SaveDpGenService")]
        public async Task<bool> SaveDpGenService(string pid, string pname, string ob_col_types,string ob_col, string selectcol, string keyName, string fname, string col_data)
        {
            bool isUpdate = false;
            bool isQi = false;
            log.Info("SendGanSyncService API");
            log.Info("SendGanSyncService API selectvaluecol :" + selectcol);
            log.Info("欄位屬性設定 :" + ob_col);
            log.Info("欄位屬性類別 :" + ob_col_types);
            log.Info("選擇欄位設定 :" + selectcol);
            log.Info("KEY欄位設定 :" + keyName);
            log.Info("FileName  :" + fname);
            //log.Info("FileName  :" + fname);
            log.Info("col_data  :" + col_data);

            if (pid == "")
            {
                isUpdate = false;
            }
            if (ob_col == "")
            {
                isUpdate = false;
            }
            if (selectcol == "")
            {
                isUpdate = false;
            }

            try
            {
                //更新col
                //selectcol = "Age,fnlwgt,hours_per_week";
                //ob_col = "C,C,C";
                //fname = "adults.csv";
                //pname = pname + "_19999";
                string newqi = "";
                if (!string.IsNullOrEmpty(ob_col))
                {
                    var obcolArray = ob_col.Split(',');
                    // string newqi = string.Join(",", selectcol.Split(',').Select(item => item + "-1"));
                    //更新col
                    newqi = string.Join(",", selectcol.Split(',').Select(item =>
                  item + (obcolArray.Contains(item) ? "-1" : "-2")));
                }
                else
                {
                    newqi = string.Join(",", selectcol.Split(',').Select(item => item + "-2"));
                }

                var col_name_arr = selectcol.Split(",");
                var col_types = ob_col_types.Split(",");
                var corr_col = selectcol.Replace(',', '^');
                var updatestresult = projService.UpdateProjectColumnTypeCorr(int.Parse(pid), pname, ob_col_types, selectcol, corr_col);
                if (updatestresult)
                {
                    //JSON
                    var lstST = proj_Service.SelectProjSampleqi_table(pid);
                    if (lstST != null)
                    {
                        if (lstST.Count > 0)
                        {
                            //update
                            var upqi = proj_Service.UpdateProjectSampleTableqi(pid, newqi, "", "", fname, pname);
                            if (!upqi)
                            {
                                isUpdate = false;
                            }
                            else
                            {
                                isUpdate = true;
                            }
                        }
                        else
                        {
                            //insert
                            //update
                            var isqi = proj_Service.InsertProjectSampleTableqi(pid, newqi, "", "", fname, pname);
                            if (!isqi)
                            {
                                isUpdate = false;
                            }
                            else
                            {
                                isUpdate = true;
                            }
                        }
                    }
                    else
                    {
                        //insert
                        //update
                        var isqi = proj_Service.InsertProjectSampleTableqi(pid, newqi, "", "", fname, pname);
                        if (!isqi)
                        {
                            isUpdate = false;
                        }
                        else
                        {
                            isUpdate = true;
                        }

                    }
                    var up5Data = projService.UpdateProjectSample5DataSelectCol(int.Parse(pid), pname, selectcol);
                    if (up5Data) 
                    {

                        var prostatus = mydbhelper.UpdateProjectStauts(int.Parse(pid), 3, "資料概化處理");
                        if (prostatus)
                            isUpdate = true;
                    }
                    else
                    {
                        isUpdate = false;
                    }
                    //string newkey = "";
                    //var newkey_arr = newkey.Split(',');
                    //var coldata_arr = col_data.Split(',');
                    //var selectvalue_arr = ob_col.Split(',');
                    //string[] ob_col_arr = null;
                    //if (!string.IsNullOrEmpty(ob_col))
                    //{
                    //    ob_col_arr = ob_col.Split(',');
                    //}
                    //var selectcol_arr = selectcol.Split(',');
                    ////var key_arr = keyName.Split(',');
                    //string strcolarr = JsonHelper.SerializeObject(coldata_arr);
                    ////var strcolarr = "[" + colarr + "]";
                    ////var jarrydataInfo = JArray.Parse(strdataInfo);

                    ////colName : 類別型欄位 keyName 傳空值
                    //dpsyncModelAPI gansyncapi = new dpsyncModelAPI
                    //{
                    //    userID = "1",
                    //    projID = pid,
                    //    projName = pname,
                    //    fileName = fname,
                    //    colNames = coldata_arr,
                    //    select_colNames = selectcol_arr,
                    //    select_colValues = selectvalue_arr

                    //};

                    //string serverfolderstr = JsonHelper.SerializeObject(gansyncapi);
                    //log.Info("genData_async :" + serverfolderstr);
                    ////  string serverfolderstr = JsonHelper.SerializeObject(serverfolder);
                    //string jsondic = JsonHelper.SerializeObject(serverfolderstr);
                    ////  string pythonstr = "{\"projName\": \"test_import_all\", \"projStep\": \"getServerFolder\", \"projID\": \"1\"}";
                    ////byte[] byteServer = Encoding.GetEncoding("utf-8").GetBytes(serverfolderstr);
                    //byte[] byteServer = Encoding.GetEncoding("utf-8").GetBytes(serverfolderstr);

                    ////參數編成 Base64 字串
                    //string JsonServer = Convert.ToBase64String(byteServer);

                    //APIModel apiModel = new APIModel();
                    //apiModel.jsonBase64 = JsonServer;

                    //string strapi = JsonHelper.SerializeObject(apiModel);
                    ////var apirestult=HttpHelper.PostUrl("getServerFolder", "{\"jsonBase64\":\"eyJwcm9qTmFtZSI6ICJ0ZXN0X2ltcG9ydF9hbGwiLCAicHJvalN0ZXAiOiAiZ2V0U2VydmVyRm9sZGVyIiwgInByb2pJRCI6ICIxIn0=\"}");                
                    //var apirestult = HttpHelper.PostUrl("DP_async", strapi);
                    //log.Info("gansync_servie return base64:" + apirestult);
                    //JObject apiresultJsobj = JObject.Parse(apirestult);
                    //string state = apiresultJsobj["STATE"].ToString();
                    //if (state == "FAILURE")
                    //{
                    //    var prostatus = mydbhelper.UpdateProjectStauts(int.Parse(pid), 99, "資料差分隱私錯誤錯誤");
                    //    string errmsg = apiresultJsobj["err"].ToString();
                    //    log.Error("genData_async State Error :" + state);
                    //    return false;
                    //}
                    //else
                    //{
                    //    Thread.Sleep(6000);
                    //    log.Info("sleep finish");

                    //    //更新欄位
                    //    var up5Data = projService.UpdateProjectSample5DataSelectCol(int.Parse(pid), pname, selectcol);
                    //    if (up5Data)
                    //    {
                    //        var prostatus = mydbhelper.UpdateProjectStauts(int.Parse(pid), 4, "資料關聯欄位處理");
                    //        if (prostatus)
                    //            isUpdate = true;
                    //    }
                    //    else
                    //    {
                    //        isUpdate = false;
                    //    }
                    //}
                    //JSON
                    //call dp api
                    //var prostatus = mydbhelper.UpdateProjectStauts(int.Parse(pid), 3, "資料運算中");
                    //if (prostatus)
                    //    isUpdate = true;


                    //// 發送 HTTP 請求到外部 API
                    //var apiName = "api/de-identification/";  // 替換成實際的 API 名稱
                    //var data_path = "static/test/" + fname;
                    //var apiBody = new
                    //{
                    //    data_path = data_path,
                    //    //task_name = pname,
                    //    task_name = pname,
                    //    selected_attrs = new
                    //    {
                    //        names = col_name_arr,
                    //        types = col_types
                    //    },
                    //    opted_cluster = new string[0],
                    //    white_list = new string[0]
                    //};

                    //var result = await _dpconn.postasync(apiName, apiBody);
                    //log.Info("SendDpService return :" + result);
                    ////var jsonResponse = JsonConvert.DeserializeObject<MyResponseModel>(result);
                    //JObject apiresultJsobj = JObject.Parse(result);
                    //// JObject apiresultJsobj = JObject.Parse(apirestult);
                    //string status = apiresultJsobj["status"].ToString();
                    //if (status == "1")
                    //{
                    //    //新增task 成功
                    //    string task_id = apiresultJsobj["task_id"].ToString();
                    //    //UpdateProjectftaskid
                    //    var assstatus = mydbhelper.UpdateProjectftaskid(int.Parse(pid), int.Parse(task_id));
                    //    //update project
                    //    var upstatuspr = mydbhelper.UpdateProjectStauts(int.Parse(pid), 4, "選擇關聯欄位");
                    //    isUpdate = true;
                    //}
                }
            }
            catch (Exception ex)
            {
                string errormsg = ex.Message.ToString();
                log.Error("SendDpSyncService Exception :" + errormsg);
                isUpdate = false;
            }
            return isUpdate;
        }

        [HttpGet("SaveDpService")]
        public async Task<bool> SaveDpService(string pid, string pname, string ob_col, string selectcol, string keyName, string fname, string col_data)
        {
            bool isUpdate = false;
            bool isQi = false;
            log.Info("SendGanSyncService API");
            log.Info("SendGanSyncService API selectvaluecol :" + selectcol);
            log.Info("欄位屬性設定 :" + ob_col);
            log.Info("選擇欄位設定 :" + selectcol);
            log.Info("KEY欄位設定 :" + keyName);
            log.Info("FileName  :" + fname);
            //log.Info("FileName  :" + fname);
            log.Info("col_data  :" + col_data);

            if (pid == "")
            {
                isUpdate = false;
            }
            if (ob_col == "")
            {
                isUpdate = false;
            }
            if (selectcol == "")
            {
                isUpdate = false;
            }

            try
            {
                //更新col
                //selectcol = "Age,fnlwgt,hours_per_week";
                //ob_col = "C,C,C";
                //fname = "adults.csv";
                //pname = pname + "_19999";
                var col_name_arr = selectcol.Split(",");
                var col_types = ob_col.Split(",");
                var corr_col = selectcol.Replace(',', '^');
                var updatestresult = projService.UpdateProjectColumnTypeCorr(int.Parse(pid), pname, ob_col, selectcol, corr_col);
                if (updatestresult)
                {
                    //JSON
                    var up5Data = projService.UpdateProjectSample5DataSelectCol(int.Parse(pid), pname, selectcol);
                    if (up5Data)
                    {
                        var prostatus = mydbhelper.UpdateProjectStauts(int.Parse(pid), 3, "資料概化處理");
                        if (prostatus)
                            isUpdate = true;
                    }
                    else
                    {
                        isUpdate = false;
                    }
                    //string newkey = "";
                    //var newkey_arr = newkey.Split(',');
                    //var coldata_arr = col_data.Split(',');
                    //var selectvalue_arr = ob_col.Split(',');
                    //string[] ob_col_arr = null;
                    //if (!string.IsNullOrEmpty(ob_col))
                    //{
                    //    ob_col_arr = ob_col.Split(',');
                    //}
                    //var selectcol_arr = selectcol.Split(',');
                    ////var key_arr = keyName.Split(',');
                    //string strcolarr = JsonHelper.SerializeObject(coldata_arr);
                    ////var strcolarr = "[" + colarr + "]";
                    ////var jarrydataInfo = JArray.Parse(strdataInfo);

                    ////colName : 類別型欄位 keyName 傳空值
                    //dpsyncModelAPI gansyncapi = new dpsyncModelAPI
                    //{
                    //    userID = "1",
                    //    projID = pid,
                    //    projName = pname,
                    //    fileName = fname,
                    //    colNames = coldata_arr,
                    //    select_colNames = selectcol_arr,
                    //    select_colValues = selectvalue_arr

                    //};

                    //string serverfolderstr = JsonHelper.SerializeObject(gansyncapi);
                    //log.Info("genData_async :" + serverfolderstr);
                    ////  string serverfolderstr = JsonHelper.SerializeObject(serverfolder);
                    //string jsondic = JsonHelper.SerializeObject(serverfolderstr);
                    ////  string pythonstr = "{\"projName\": \"test_import_all\", \"projStep\": \"getServerFolder\", \"projID\": \"1\"}";
                    ////byte[] byteServer = Encoding.GetEncoding("utf-8").GetBytes(serverfolderstr);
                    //byte[] byteServer = Encoding.GetEncoding("utf-8").GetBytes(serverfolderstr);

                    ////參數編成 Base64 字串
                    //string JsonServer = Convert.ToBase64String(byteServer);

                    //APIModel apiModel = new APIModel();
                    //apiModel.jsonBase64 = JsonServer;

                    //string strapi = JsonHelper.SerializeObject(apiModel);
                    ////var apirestult=HttpHelper.PostUrl("getServerFolder", "{\"jsonBase64\":\"eyJwcm9qTmFtZSI6ICJ0ZXN0X2ltcG9ydF9hbGwiLCAicHJvalN0ZXAiOiAiZ2V0U2VydmVyRm9sZGVyIiwgInByb2pJRCI6ICIxIn0=\"}");                
                    //var apirestult = HttpHelper.PostUrl("DP_async", strapi);
                    //log.Info("gansync_servie return base64:" + apirestult);
                    //JObject apiresultJsobj = JObject.Parse(apirestult);
                    //string state = apiresultJsobj["STATE"].ToString();
                    //if (state == "FAILURE")
                    //{
                    //    var prostatus = mydbhelper.UpdateProjectStauts(int.Parse(pid), 99, "資料差分隱私錯誤錯誤");
                    //    string errmsg = apiresultJsobj["err"].ToString();
                    //    log.Error("genData_async State Error :" + state);
                    //    return false;
                    //}
                    //else
                    //{
                    //    Thread.Sleep(6000);
                    //    log.Info("sleep finish");

                    //    //更新欄位
                    //    var up5Data = projService.UpdateProjectSample5DataSelectCol(int.Parse(pid), pname, selectcol);
                    //    if (up5Data)
                    //    {
                    //        var prostatus = mydbhelper.UpdateProjectStauts(int.Parse(pid), 4, "資料關聯欄位處理");
                    //        if (prostatus)
                    //            isUpdate = true;
                    //    }
                    //    else
                    //    {
                    //        isUpdate = false;
                    //    }
                    //}
                    //JSON
                    //call dp api
                    //var prostatus = mydbhelper.UpdateProjectStauts(int.Parse(pid), 3, "資料運算中");
                    //if (prostatus)
                    //    isUpdate = true;


                    //// 發送 HTTP 請求到外部 API
                    //var apiName = "api/de-identification/";  // 替換成實際的 API 名稱
                    //var data_path = "static/test/" + fname;
                    //var apiBody = new
                    //{
                    //    data_path = data_path,
                    //    //task_name = pname,
                    //    task_name = pname,
                    //    selected_attrs = new
                    //    {
                    //        names = col_name_arr,
                    //        types = col_types
                    //    },
                    //    opted_cluster = new string[0],
                    //    white_list = new string[0]
                    //};

                    //var result = await _dpconn.postasync(apiName, apiBody);
                    //log.Info("SendDpService return :" + result);
                    ////var jsonResponse = JsonConvert.DeserializeObject<MyResponseModel>(result);
                    //JObject apiresultJsobj = JObject.Parse(result);
                    //// JObject apiresultJsobj = JObject.Parse(apirestult);
                    //string status = apiresultJsobj["status"].ToString();
                    //if (status == "1")
                    //{
                    //    //新增task 成功
                    //    string task_id = apiresultJsobj["task_id"].ToString();
                    //    //UpdateProjectftaskid
                    //    var assstatus = mydbhelper.UpdateProjectftaskid(int.Parse(pid), int.Parse(task_id));
                    //    //update project
                    //    var upstatuspr = mydbhelper.UpdateProjectStauts(int.Parse(pid), 4, "選擇關聯欄位");
                    //    isUpdate = true;
                    //}
                }
            }
            catch (Exception ex)
            {
                string errormsg = ex.Message.ToString();
                log.Error("SendDpSyncService Exception :" + errormsg);
                isUpdate = false;
            }
            return isUpdate;
        }


        [HttpGet("SendDpService")]
        public async Task<bool> SendDpService(string pid, string pname, string ob_col, string selectcol, string keyName, string fname, string col_data)
        {
            bool isUpdate = false;
            bool isQi = false;
            log.Info("SendGanSyncService API");
            log.Info("SendGanSyncService API selectvaluecol :" + selectcol);
            log.Info("欄位屬性設定 :" + ob_col);
            log.Info("選擇欄位設定 :" + selectcol);
            log.Info("KEY欄位設定 :" + keyName);
            log.Info("FileName  :" + fname);
            //log.Info("FileName  :" + fname);
            log.Info("col_data  :" + col_data);

            if (pid == "")
            {
                isUpdate = false;
            }
            if (ob_col == "")
            {
                isUpdate = false;
            }
            if (selectcol == "")
            {
                isUpdate = false;
            }

            try
            {
                //更新col
                //selectcol = "Age,fnlwgt,hours_per_week";
                //ob_col = "C,C,C";
                //fname = "adults.csv";
                //pname = pname + "_19999";
                var col_name_arr = selectcol.Split(",");
                var col_types = ob_col.Split(",");
                var corr_col = selectcol.Replace(',', '^');
                var updatestresult = projService.UpdateProjectColumnTypeCorr(int.Parse(pid), pname, ob_col, selectcol,corr_col);
                if (updatestresult)
                {
                    //JSON
                    string newkey = "";
                    var newkey_arr = newkey.Split(',');
                    var coldata_arr = col_data.Split(',');
                    var selectvalue_arr = ob_col.Split(',');
                    string[] ob_col_arr = null;
                    if (!string.IsNullOrEmpty(ob_col))
                    {
                        ob_col_arr = ob_col.Split(',');
                    }
                    var selectcol_arr = selectcol.Split(',');
                    //var key_arr = keyName.Split(',');
                    string strcolarr = JsonHelper.SerializeObject(coldata_arr);
                    //var strcolarr = "[" + colarr + "]";
                    //var jarrydataInfo = JArray.Parse(strdataInfo);

                    //colName : 類別型欄位 keyName 傳空值
                    dpsyncModelAPI gansyncapi = new dpsyncModelAPI
                    {
                        userID = "1",
                        projID = pid,
                        projName = pname,
                        fileName = fname,
                        colNames = coldata_arr,
                        select_colNames = selectcol_arr,
                        select_colValues = selectvalue_arr

                    };

                    string serverfolderstr = JsonHelper.SerializeObject(gansyncapi);
                    log.Info("genData_async :" + serverfolderstr);
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
                    var apirestult = HttpHelper.PostUrl("DP_async", strapi);
                    log.Info("gansync_servie return base64:" + apirestult);
                    JObject apiresultJsobj = JObject.Parse(apirestult);
                    string state = apiresultJsobj["STATE"].ToString();
                    if (state == "FAILURE")
                    {
                        var prostatus = mydbhelper.UpdateProjectStauts(int.Parse(pid), 99, "資料差分隱私錯誤錯誤");
                        string errmsg = apiresultJsobj["err"].ToString();
                        log.Error("genData_async State Error :" + state);
                        return false;
                    }
                    else
                    {
                         //Thread.Sleep(6000);
                        log.Info("sleep finish");

                        //更新欄位
                        var up5Data = projService.UpdateProjectSample5DataSelectCol(int.Parse(pid), pname, selectcol);
                        if (up5Data)
                        {
                            //var prostatus = mydbhelper.UpdateProjectStauts(int.Parse(pid), 4, "資料關聯欄位處理");
                            //if (prostatus)
                                isUpdate = true;
                        }
                        else
                        {
                            isUpdate = false;
                        }
                    }
                    //JSON
                    //call dp api
                    //var prostatus = mydbhelper.UpdateProjectStauts(int.Parse(pid), 3, "資料運算中");
                    //if (prostatus)
                    //    isUpdate = true;


                    //// 發送 HTTP 請求到外部 API
                    //var apiName = "api/de-identification/";  // 替換成實際的 API 名稱
                    //var data_path = "static/test/" + fname;
                    //var apiBody = new
                    //{
                    //    data_path = data_path,
                    //    //task_name = pname,
                    //    task_name = pname,
                    //    selected_attrs = new
                    //    {
                    //        names = col_name_arr,
                    //        types = col_types
                    //    },
                    //    opted_cluster = new string[0],
                    //    white_list = new string[0]
                    //};

                    //var result = await _dpconn.postasync(apiName, apiBody);
                    //log.Info("SendDpService return :" + result);
                    ////var jsonResponse = JsonConvert.DeserializeObject<MyResponseModel>(result);
                    //JObject apiresultJsobj = JObject.Parse(result);
                    //// JObject apiresultJsobj = JObject.Parse(apirestult);
                    //string status = apiresultJsobj["status"].ToString();
                    //if (status == "1")
                    //{
                    //    //新增task 成功
                    //    string task_id = apiresultJsobj["task_id"].ToString();
                    //    //UpdateProjectftaskid
                    //    var assstatus = mydbhelper.UpdateProjectftaskid(int.Parse(pid), int.Parse(task_id));
                    //    //update project
                    //    var upstatuspr = mydbhelper.UpdateProjectStauts(int.Parse(pid), 4, "選擇關聯欄位");
                    //    isUpdate = true;
                    //}
                }
            }
            catch (Exception ex)
            {
                string errormsg = ex.Message.ToString();
                log.Error("SendDpSyncService Exception :" + errormsg);
                isUpdate = false;
            }
            return isUpdate;
        }


        [HttpGet("checkdataassocation")]
        public async Task<bool> checkdataassocation(string pid, string selectcol)
        {
            bool isUpdate = false;
            bool isQi = false;
            log.Info("SendGanSyncService API");
            log.Info("checkdataassocation API selectvaluecol :" + selectcol);


            if (pid == "")
            {
                isUpdate = false;
            }

            if (selectcol == "")
            {
                isUpdate = false;
            }

            try
            {
                
                //更新col
                if(selectcol != null)
                {

                }
               //// var col_name_arr = selectcol.Split(",");
               // var col_types = selectcol.Split(",");
                // var new_choose_corr = selectcol.Replace(",", "^");
               // var new_choose_corr = "";
                //new_choose_corr= "[\"" +selectcol +"\"]";
                var updatecoltype = proj_Service.UpdateProjectColumnDPCol(pid, selectcol);
                if(updatecoltype)
                {
                    var prostatus = mydbhelper.UpdateProjectStauts(int.Parse(pid), 6, "資料關聯儲存");
                }
                isUpdate = true;
                //var 
                //JSON
                //call dp api
                //var prostatus = mydbhelper.UpdateProjectStauts(int.Parse(pid), 5, "資料關聯中");
                //if (prostatus)
                //    isUpdate = true;
                //var lstST = proj_Service.SelectProjSample5TB(pid);
                //log.Info("ML DataRow Count :" + lstST.Count());
                //var pname = "";
                //var fname = "";
                //int task_id = 0;
                //var selectcol_name = "";
                //var selectcolvalue = "";

                //if (lstST.Count > 0)
                //{
                //    foreach (var item in lstST)
                //    {
                //        pname = item.project_name;
                //        fname = item.file_name;
                //        task_id = item.ftaskid;
                //        selectcol_name = item.selectcol;
                //        selectcolvalue = item.selectcolvalue;
                //    }
                //}
                ////selectcol_name = "Age,fnlwgt,hours_per_week";
                ////selectcolvalue = "C,C,C";
                ////fname = "adults.csv";
                ////pname = pname + "_19999";
                //selectcol = selectcol_name;
                //var names_arr = selectcol_name.Split(",").ToList();
                //var tpyes_arr = selectcolvalue.Split(",");
                //var opted_cluster_arr = selectcol.Split(',');
                //var jsonDataObject = new
                //{
                //    opted_cluster = opted_cluster_arr.Select(item => new[] { item }).ToArray()
                //};

                //// 發送 HTTP 請求到外部 API
                //var apiName = "api/de-identification/" + task_id.ToString() + "/";  // 替換成實際的 API 名稱
                ////var apiName = "api/de-identification/" +"485/";  // 替換成實際的 API 名稱
                //var data_path = "static/test/" + fname;
                //var apiBody = new
                //{
                //    data_path = data_path,
                //    task_name = pname,
                //    selected_attrs = new
                //    {
                //        names = names_arr,
                //        types = tpyes_arr
                //    },
                //    opted_cluster =
                //            jsonDataObject
                //        ,
                //    white_list = new string[0]
                //};

                //var result = await _dpconn.putasync(apiName, apiBody);
                //log.Info("checkdataassocation return :" + result);
                ////var jsonResponse = JsonConvert.DeserializeObject<MyResponseModel>(result);
                //JObject apiresultJsobj = JObject.Parse(result);
                //// JObject apiresultJsobj = JObject.Parse(apirestult);
                //string status = apiresultJsobj["status"].ToString();
                //if (result != "")
                //{
                //    //新增task 成功
                //    string sec_task_id = apiresultJsobj["task_id"].ToString();
                //    //UpdateProjectftaskid
                //    var assstatus = mydbhelper.UpdateProjectsectaskid(int.Parse(pid), int.Parse(sec_task_id));
                //    //update project
                //    var upstatuspr = mydbhelper.UpdateProjectStauts(int.Parse(pid), 5, "差分隱私處理");
                //    isUpdate = true;
                //}

            }
            catch (Exception ex)
            {
                string errormsg = ex.Message.ToString();
                log.Error("SendGanSyncService Exception :" + errormsg);
                isUpdate = false;
            }
            return isUpdate;
        }

        [HttpGet("UpdateGanStatsRead")]
        public bool UpdateGanStatsRead()
        {
            bool isUpdate = false;
            try
            {
                var jobstatusresult = mydbhelper.UpdateGanReadStauts();
                if (jobstatusresult)
                    isUpdate = true;
            }
            catch (Exception ex)
            {
                log.Error("UpdateGanStatsRead Exception :" + ex.Message);
            }
            return isUpdate;
        }

        //[HttpGet("GetGanNotification")]
        //public string GetGanNotification()
        //{
        //    int gancount = 0;
        //    string errorMsg = "";
        //    string returnmsg = "";
        //    //string returnmsg = "";
        //    //ProjectSparkMan
        //    string not_ntml = "";
        //    try
        //    { //SelectProjectGanStatus
        //        var jobcount = mydbhelper.SelectProjectGanStatus();
        //        if (jobcount == null)
        //            log.Info("Notification :" + "0筆");
        //        else
        //            log.Info("共新資料幾筆 Notification :" + jobcount.Count);

        //        var jobstatusresult = mydbhelper.SelectProjectJobStatus();
        //        if (jobstatusresult == null)
        //            log.Info("Notification :" + "0筆");
        //        else
        //            log.Info("共資料幾筆 Notification :" + jobstatusresult.Count);


        //        if (jobcount.Count > 0)
        //        {
        //            foreach (var items in jobcount)
        //            {
        //                log.Info("未讀 project_name :" + items.project_name);

        //                log.Info("未讀 job project_cht :" + items.project_cht);
        //                log.Info("未讀 job filename :" + items.file_name);
        //                log.Info("未讀 job jobname :" + items.jobname);


        //                string jobnm = "";
        //                if (items.jobname == "Preview")
        //                    jobnm = "資料匯入完成";
        //                else if (items.jobname == "GAN")
        //                    jobnm = "資料生成完成";
        //                else if (items.jobname == "MLutility")
        //                    jobnm = "可用性分析完成";
        //                else
        //                    jobnm = "資料匯出完成";

        //                not_ntml += "<li class=\"notification_dropdown_item read\">" + "<img src=\"/images/noti_light.png\">" +
        //                            "<div class=\"text\"><p>" + items.project_cht + "  " + items.jobname + "</p><div class=\"time\">" + items.gan_time.ToString("yyyy-MM-dd HH:mm:ss") + "</div></div></li>";
        //            }
        //        }


        //        if (jobstatusresult.Count > 0)
        //        {
        //            gancount = jobcount.Count;
        //            foreach (var item in jobstatusresult)
        //            {

        //                log.Info("已讀 project_name :" + item.project_name);

        //                log.Info("已讀 job project_cht :" + item.project_cht);
        //                log.Info("已讀 job filename :" + item.file_name);
        //                log.Info("已讀 job jobname :" + item.jobname);

        //                //尚未組成T_CeleryStatus
        //                string jobnm = "";
        //                if (item.jobname == "Preview")
        //                    jobnm = "資料匯入完成";
        //                else if (item.jobname == "GAN")
        //                    jobnm = "資料生成完成";
        //                else if (item.jobname == "MLutility")
        //                    jobnm = "可用性分析完成";
        //                else
        //                    jobnm = "資料匯出完成";

        //                not_ntml += "<li class=\"notification_dropdown_item read\">" + "<img src=\"/images/noti_light.png\">" +
        //                            "<div class=\"text\"><p>" + item.project_cht + "  " + jobnm + "</p><div class=\"time\">" + item.gan_time.ToString("yyyy-MM-dd HH:mm:ss") + "</div></div></li>";

        //                //var lstcelery = mydbhelper.SelectCeleryStatus(item.project_id);
        //                //if(lstcelery.Count > 0)
        //                //{
        //                //    foreach(var items in lstcelery)
        //                //    {
        //                //        var res = item.return_result.Split(',');
        //                //        if(res[res.Length-1]!="Mission Complete")
        //                //        {
        //                //            not_ntml += "<li class=\"notification_dropdown_item\">" + "<img src=\"/images/noti_light.png\">" +
        //                //                "<div class=\"text\"><p>" + item.project_cht + "  " + items.step + "</p><div class=\"time\">" + items.createtime.ToString("MM-dd") + "</div></div></li>";

        //                //        }

        //                //    }
        //                //}

        //            }
        //            string final_html = "<li class=\"notification_dropdown_item\">" + _localizer.Text.notification + "</li>" + not_ntml;
        //            returnmsg = jobcount.Count.ToString() + "*" + final_html;
        //        }
        //        else
        //        {
        //            returnmsg = jobcount.Count.ToString();
        //        }
        //    }
        //    catch (Exception ex)
        //    {
        //        log.Error("Gan Notification Exception :" + ex.Message);
        //    }
        //    // returnmsg = "0";


        //    //組成 json 

        //    //return returnmsg;
        //    return returnmsg;
        //}
        [HttpGet("SendMLutility")]
        public async Task<bool> SendMLutility(string pid, string privacy_level,string custep)
        {
            bool isUpdate = false;
            log.Info("SendMLutility API");
            log.Info("SendMLutility API privacy_level :" + privacy_level);

            log.Info("pid  :" + pid);
            //log.Info("FileName  :" + fname);

            if (pid == "")
            {
                return false;
            }
            if (privacy_level == "")
            {
                return false;
            }


            try
            {
                var lstST = proj_Service.SelectProjSample5TB(pid);
                log.Info("ML DataRow Count :" + lstST.Count());
                var pname = "";
                var fname = "";
                var colNames = "";
                var select_colNames = "";
                var choose_corr_col = "";
                var corr_col = "";
                var select_colValues = "";
                int task_id = 0;
                var selectcol_name = "";
                var selectcolvalue = "";
                var epsilon = "1";
                if (string.IsNullOrEmpty(custep))
                {
                    if (privacy_level == "1")
                    {
                        epsilon = "100";
                    }
                    else if (privacy_level == "2")
                    {
                        epsilon = "10";
                    }
                    else if(privacy_level == "3")
                    {
                        epsilon = "1";
                    }
                    else if (privacy_level =="4")
                    {
                        epsilon = custep;

                    }
                    else
                    {
                        epsilon = custep;

                    }
                }
                else
                {
                    epsilon = custep;
                }


                if (lstST.Count > 0)
                {
                    foreach (var item in lstST)
                    {
                        pname = item.project_name;
                        fname = item.file_name;
                        colNames = item.pro_col_en;
                        select_colNames = item.pro_col_cht;
                        choose_corr_col = item.choose_corr_col;
                        corr_col = item.corr_col;
                        select_colValues = item.ob_col;
                        selectcol_name = item.selectcol;
                        selectcolvalue = item.selectcolvalue;
                        
                    }
                }
                string[] emptyArray = new string[0];
                var coldata_arr = colNames.Split(',');
                var selectcol_arr = selectcol_name.Split(',');
                var selectvalue_arr = selectcolvalue.Split(',');
                var corr_col_arr = corr_col.Split(',');
                //var choose_corr_col_arr = choose_corr_col.Split(',');

                var updatestresult = projService.UpdateProjectColumnTypeEp(int.Parse(pid), epsilon);
                
                    dp_epdata_syncModelAPI gansyncapi = new dp_epdata_syncModelAPI
                {
                    userID = "1",
                    projID = pid,
                    projName = pname,
                    fileName = fname,
                    colNames = coldata_arr,
                    select_colNames = selectcol_arr,
                    select_colValues = selectvalue_arr,
                    epsilon = epsilon,
                    choose_corr_col = corr_col_arr,
                    corr_col = corr_col_arr
                  };

                string serverfolderstr = JsonHelper.SerializeObject(gansyncapi);
                log.Info("Dp_data_async :" + serverfolderstr);
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
                var apirestult = HttpHelper.PostUrl("DP_data_async", strapi);
                log.Info("gansync_servie return base64:" + apirestult);
                JObject apiresultJsobj = JObject.Parse(apirestult);
                string state = apiresultJsobj["STATE"].ToString();
                if (state == "FAILURE")
                {
                    var prostatus = mydbhelper.UpdateProjectStauts(int.Parse(pid), 99, "資料差分隱私錯誤錯誤");
                    string errmsg = apiresultJsobj["err"].ToString();
                    log.Error("genData_async State Error :" + state);
                    return false;
                }
                else
                {
                    ////更新欄位
                    //var up5Data = projService.UpdateProjectSample5DataSelectCol(int.Parse(pid), pname, selectcol);
                    //if (up5Data)
                    //{
                        var prostatus = mydbhelper.UpdateProjectStauts(int.Parse(pid), 7, "隱私強化處理中");
                        if (prostatus)
                            isUpdate = true;
                    //}
                    //else
                    //{
                    //    isUpdate = false;
                    //}
                }
                //var apiName = "api/de-identification/" + task_id.ToString() + "/job/";  // 替換成實際的 API 名稱
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

                //var result = await _dpconn.postasync(apiName, requestData);
                //log.Info("SendMLutility return :" + result);
                //log.Info("SendMLutility return :" + result);
                ////var jsonResponse = JsonConvert.DeserializeObject<MyResponseModel>(result);
                //JObject apiresultJsobj = JObject.Parse(result);
                //// JObject apiresultJsobj = JObject.Parse(apirestult);
                //string status = apiresultJsobj["status"].ToString();
                //if (status == "1")
                //{
                //    //新增task 成功
                //    string dp_id = apiresultJsobj["dp_id"].ToString();
                //    //UpdateProjectftaskid
                //    var assstatus = mydbhelper.UpdateProjectdpid(int.Parse(pid), int.Parse(dp_id));
                //    //update project
                //    var upstatuspr = mydbhelper.UpdateProjectStauts(int.Parse(pid), 6, "產生報表");
                //    isUpdate = true;
                //}
            }
            catch (Exception ex)
            {
                string errormsg = ex.Message.ToString();
                log.Error("SendMLutility Exception :" + errormsg);

            }
            return isUpdate;
        }

        [HttpGet("SendDataCheck")]
        public bool SendDataCheck(string pid, string pname, string fname, string targernm)
        {
            bool isUpdate = false;
            log.Info("SendDataCheck API");
            log.Info("SendDataCheck API targetName :" + targernm);

            log.Info("FileName  :" + fname);
            //log.Info("FileName  :" + fname);

            if (pid == "")
            {
                return false;
            }
            if (targernm == "")
            {
                return false;
            }

            var tager_arr = targernm.Split(',');
            try
            {

                //JSON
                MLDataModelAPI mlsyncapi = new MLDataModelAPI
                {
                    userID = "1",
                    projID = pid,
                    projName = pname,
                    rawDataName = fname,
                    targetCols = tager_arr

                };

                string serverfolderstr = JsonHelper.SerializeObject(mlsyncapi);
                log.Info("MLutility_async :" + serverfolderstr);
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
                var prostatus = mydbhelper.UpdateProjectStauts(int.Parse(pid), 7, "資料可用性分析中");
                    //var apirestult=HttpHelper.PostUrl("getServerFolder", "{\"jsonBase64\":\"eyJwcm9qTmFtZSI6ICJ0ZXN0X2ltcG9ydF9hbGwiLCAicHJvalN0ZXAiOiAiZ2V0U2VydmVyRm9sZGVyIiwgInByb2pJRCI6ICIxIn0=\"}");                
                    var apirestult = HttpHelper.PostUrl("MLutility_async", strapi);
                log.Info("MLutility_async return base64:" + apirestult);
                JObject apiresultJsobj = JObject.Parse(apirestult);
                // JObject apiresultJsobj = JObject.Parse(apirestult);
                string state = apiresultJsobj["STATE"].ToString();
                if (state == "FAILURE")
                {
                    var upprostatus = mydbhelper.UpdateProjectStauts(int.Parse(pid), 98, "資料相似度錯誤");

                    string errmsg = apiresultJsobj["err"].ToString();
                    log.Error("MLutility_async State Error :" + state);
                    return false;
                }
                else
                {
                    //更新欄位
                    var up5Data = projService.UpdateProjectSample5DataTarget(int.Parse(pid), pname, targernm);
                    if (up5Data)
                    {
                        
                            isUpdate = true;
                    }
                    else
                    {
                        isUpdate = false;
                    }
                }

            }
            catch (Exception ex)
            {
                string errormsg = ex.Message.ToString();
                log.Error("SendDataCheck Exception :" + errormsg);

            }
            return isUpdate;
        }


        [HttpGet("AddDept")]
        public int AddDept(string deptname)
        {
            bool isAdd = false;
            try
            {
                log.Info("AddDept deptname :" + deptname);
                var deptlist = mydbhelper.selectDept(deptname);
                if (deptlist.Count > 0)
                {
                    //有重複
                    return -2;
                }
                else
                {
                    var dpstatus = mydbhelper.InsertDept(deptname);
                    if (dpstatus)
                        return 1;
                    else
                        return -1;
                }
            }
            catch (Exception ex)
            {
                string errormsg = ex.Message.ToString();
                log.Error("AddDept Exception :" + errormsg);
                return -99;
            }

        }
        [HttpGet("ChangeLang")]
        public bool ChangeLang(string lan)
        {
            string c = "";

            if (lan == "tw")
                c = "zh-TW";
            else
                c = "en-US";
            string lang = CookieRequestCultureProvider.MakeCookieValue(new RequestCulture(c));
            Response.Cookies.Append(CookieRequestCultureProvider.DefaultCookieName, lang);
            //return RedirectToAction("Index", "Home");//重新導向至Index Action
            return true;
        }

        [HttpGet("ImportData")]
        public string ImportData(string pname, string pid, string filenames)
        {
            string returnmsg = "";
            log.Info("Web API ImportData Gen API Preview");
            log.Info("pid " + pid);
            log.Info("pname " + pname);
            try
            {
                //"{\"projName\": \"test_import_all\", \"projStep\": \"import\", \"projID\": \"1\"}"
                previewDataModelAPI previewData = new previewDataModelAPI
                {
                    userID = "1",
                    projID = pid,
                    projName = pname,
                    //serverfolder.projName = "test_import_all";
                    fileName = filenames,

                };
                string serverfolderstr = JsonHelper.SerializeObject(previewData);
                log.Info("PreviewDatra Json String :" + serverfolderstr);
                // string pythonstr = "{\"projName\": \"test_import_all\", \"projStep\": \"getServerFolder\", \"projID\": \"1\"}";
                byte[] byteServer = Encoding.GetEncoding("utf-8").GetBytes(serverfolderstr);

                //參數編成 Base64 字串
                string JsonServer = Convert.ToBase64String(byteServer);

                APIModel apiModel = new APIModel
                {
                    jsonBase64 = JsonServer
                };

                string strapi = JsonHelper.SerializeObject(apiModel);
                //var apirestult=HttpHelper.PostUrl("getServerFolder", "{\"jsonBase64\":\"eyJwcm9qTmFtZSI6ICJ0ZXN0X2ltcG9ydF9hbGwiLCAicHJvalN0ZXAiOiAiZ2V0U2VydmVyRm9sZGVyIiwgInByb2pJRCI6ICIxIn0=\"}");                
                log.Info("PreviewDatra Json String " + strapi);
                var apirestult = HttpHelper.PostUrl("preview_async", strapi);
                log.Info("PreviewDatra Json  Return String " + apirestult);

                JObject apiresultJsobj = JObject.Parse(apirestult);
                string state = apiresultJsobj["STATE"].ToString();
                if (state == "FAIL")
                {

                    string errmsg = apiresultJsobj["ERRMSG"].ToString();
                    log.Error("preview_async State Error :" + state);
                    return "-1";
                }

                //string apibase641 = apiresultJsobj["jsonBase64"].ToString();
                //var jsapiresults = Encoding.UTF8.GetString(Convert.FromBase64String(apibase641));
                //log.Info("PreviewDatra return JsonString :" + jsapiresults);
                //JObject apidecode = JObject.Parse(jsapiresults);
                //string apistatus = apidecode["status"].ToString();
                //if (apistatus == "1")
                //{
                //    List<ProjectSparkMan> ojString = new List<ProjectSparkMan>();
                //    ProjectSparkMan psman = new ProjectSparkMan();
                //    psman.celery_id = apidecode["celeryID"].ToString();
                //    psman.app_id = apidecode["sparkAppID"].ToString();
                //    psman.step = "ImportFile";
                //    psman.stepstatus = 0;
                //    //TODO
                //    //增加欄位 step  用已確認步驟
                //    psman.project_id = int.Parse(pid);
                //    log.Info("celeryID : " + apidecode["celeryID"].ToString());
                //    log.Info("sparkAppID : " + apidecode["sparkAppID"].ToString());
                //    log.Info("step : " + "ImportFile");
                //    log.Info("stepstatus :0");
                //    ojString.Add(psman);
                //    var sparkstatus = mydbhelper.InsertSparkStauts(ojString);

                //    //更新系統狀態
                //    if (sparkstatus)
                //    {
                var prostatus = mydbhelper.UpdateProjectStauts(int.Parse(pid), 2, "選擇資料生成欄位");
                if (prostatus)
                    returnmsg = "1";
                //    }
                //    else
                //    {
                //        string errMsg = "-1";
                //        returnmsg = errMsg;
                //    }
                //}
                //else
                //{
                //    string errMsg = apidecode["errMsg"].ToString();
                //    log.Error("ImportFile Return Json Error :" + errMsg);
                //    returnmsg = "-2";
                //}

                //"{\"status\": \"1\", \"celeryID\": \"14ed2515-6fa3-46b1-bb7a-3023dc26146c\", \"tblNames\": \"adult_id;adult_id_adult_testNA2;adult_id_post2w;
                //adult;adult_id_pre2w\", \"projStep\": \"import\", \"time_async\": \"15.817054987\", \"sparkAppID\": \"application_1547630236814_0197\", \"dbName\": \"test_import_all\", \"errMsg\": \"\"}"
                //returnmsg = "1";
                return returnmsg;
            }
            catch (Exception ex)
            {
                log.Error("ImportFile Exception :" + ex.Message);
                return "-2";
            }
        }


        [HttpGet("ExportData")]
        public bool ExportData(string pid, string pname, string selectcsv)
        {
            // string returnmsg = "";
            log.Info("Web API ExportData");
            log.Info("pid " + pid);
            log.Info("pname " + pname);
            log.Info("selectcsv " + selectcsv);
            var selectcsv_arr = selectcsv.Split(',');
            string projStep = "export";
            try
            {
                ExportFileAPI exportfile = new ExportFileAPI
                {
                    userID = "1",
                    projID = pid,
                    projName = pname,
                    dataName = selectcsv_arr

                };

                string serverfolderstr = JsonHelper.SerializeObject(exportfile);
                log.Info("export file :" + serverfolderstr);
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
                // var apirestult = HttpHelper.PostUrl("exportData_async", strapi);
                var apirestult = HttpHelper.PostUrl("PETs_exportData_async", strapi);
                log.Info("exportData_async return base64:" + apirestult);

                JObject apiresultJsobj = JObject.Parse(apirestult);
                //JObject apiresultJsobj = JObject.Parse(apirestult);
                string state = apiresultJsobj["STATE"].ToString();
                if (state == "FAIL")
                {
                    ViewData["file"] = "";
                    string errmsg = apiresultJsobj["ERRMSG"].ToString();
                    log.Error("exportData_async State Error :" + state);
                }
                else
                {
                    var prostatus = mydbhelper.UpdateProjectStauts(int.Parse(pid), 7, "匯出資料中....");
                    //if (prostatus)

                }

                return true;
            }
            catch (Exception ex)
            {
                log.Error("Export File Exception :" + ex.Message);
                return false;
            }
        }
        [HttpGet("UpdateNotificationStatus")]
        public bool UpdateNotificationStatus()
        {
            bool isUpdate = false;
            try
            {
                var prostatus = mydbhelper.UpdateProjectStauts(int.Parse(""), 8, "去識別化作業完成....");
                if (prostatus)
                {
                    isUpdate = true;
                }

            }
            catch (Exception ex)
            {

            }
            return isUpdate;
        }

        [HttpGet("GetNotificationData")]
        public string GetNotificationData()
        {
            string returnmsg = "";
            //ProjectSparkMan
            string not_ntml = "";
            var jobstatusresult = mydbhelper.SelectProjectJobStatus();
            log.Info("GetNotificationData");
            if (jobstatusresult == null)
                log.Info("Notification :" + "0筆");
            else
                log.Info("共幾筆 Notification :" + jobstatusresult.Count);
            if (jobstatusresult.Count > 0)
            {
                foreach (var item in jobstatusresult)
                {
                    try
                    {
                        log.Info("project_name :" + item.project_name);

                        log.Info("job project_cht :" + item.project_cht);
                        log.Info("job filename :" + item.file_name);
                        log.Info("job jobname :" + item.jobname);
                        log.Info("job jobname :" + item.statustime);

                        //尚未組成T_CeleryStatus

                        not_ntml += "<li class=\"notification_dropdown_item\"><div class=\"noti_date\"><h6>" + item.statustime.ToString("MM-dd") + "</h6></div>" +
                                            "<div class=\"text\"><p>" + item.project_cht + "_" + item.project_name + " : " + item.jobname + "</p></div></li>";
                    }
                    catch (Exception ex)
                    {
                        log.Error("Notification Exception :" + ex.Message);
                        //  return false;
                    }
                }
            }

            string final_html = "<li class=\"notification_dropdown_item\">" + _localizer.Text.notification + "</li>" + not_ntml;
            returnmsg = jobstatusresult.Count.ToString() + "*" + final_html;

            //組成 json 

            return returnmsg;
        }



        [HttpGet("InsertProject")]
        public string InsertProject(string pname, string prodesc, string pinput, string poutput, string powner, string p_dsname)
        {
            try
            {
                log.Info("WebAPI 建立專案 名稱:" + pname);
                log.Info("WebAPI 建立專案 描述:" + prodesc);
                log.Info("WebAPI 建立專案 中文名稱:" + p_dsname);

                string chtsql = "select * from T_Project where project_cht='" + p_dsname + "'";
                log.Info("WebAPI InsertProject 專案名稱中文 Sql :" + chtsql);
                var prochtlist = mydbhelper.SelectProject(chtsql);
                log.Info("project name 重複筆數 :" + prochtlist.Count.ToString());
                if (prochtlist.Count > 0)
                {
                    return "-5";
                }

                string sql = "select * from T_Project where project_name='" + pname + "'";
                log.Info("WebAPI InsertProject Sql :" + sql);
                var prolist = mydbhelper.SelectProject(sql);
                log.Info("project name 重複筆數 :" + prolist.Count.ToString());
                if (prolist.Count > 0)
                {
                    return "-2";
                }
                string project_path = "static/test/";

                pinput = project_path;
                string insertsql = "insert into T_Project(project_name,project_desc,project_path,export_path,projectowner_id,createtime,project_cht)values('" + pname + "','" + prodesc + "','" + pinput + "','" + poutput + "'," + powner + ",Now(),'" + p_dsname + "');";
                var result = mydbhelper.InsertDB(insertsql);
                if (result)
                {
                    var proId = mydbhelper.SelectProject(sql);
                    foreach (var item in proId)
                    {
                        log.Info("WebAPI InsertProject Insert ProjectStatus ");

                        //var prostatussql = "insert into T_ProjectStatus(project_id,project_status,statusname,createtime)values(" + item.Project_id + ",0,'資料匯入處理中',now())";
                        var psresult = projService.InsertProjectStauts(item.Project_id, 0, "資料專案開啟");

                        if (!psresult)
                        {
                            return "-3";
                        }

                        //gen 生成API
                        //'{'userID':'JOJO','projID': '9517', 'projName': 'adult'}'
                        var jsoncreatefolder = "";
                        createFolderAPI cfolder = new createFolderAPI
                        {
                            userID = "1",
                            projID = item.Project_id.ToString(),
                            //serverfolder.projName = "test_import_all";
                            projName = item.project_name
                        };
                        string serverfolderstr = JsonHelper.SerializeObject(cfolder);
                        log.Info("Sync createFolder Json String :" + serverfolderstr);
                        //string pythonstr = "{\"projName\": \"test_import_all\", \"projStep\": \"getServerFolder\", \"projID\": \"1\"}";
                        //byte[] byteServer = Encoding.GetEncoding("utf-8").GetBytes(pythonstr);
                        byte[] byteServer = Encoding.GetEncoding("utf-8").GetBytes(serverfolderstr);

                        //參數編成 Base64 字串
                        string JsonServer = Convert.ToBase64String(byteServer);

                        APIModel apiModel = new APIModel
                        {
                            jsonBase64 = JsonServer
                        };

                        string strapi = JsonHelper.SerializeObject(apiModel);
                        //var apirestult=HttpHelper.PostUrl("getServerFolder", "{\"jsonBase64\":\"eyJwcm9qTmFtZSI6ICJ0ZXN0X2ltcG9ydF9hbGwiLCAicHJvalN0ZXAiOiAiZ2V0U2VydmVyRm9sZGVyIiwgInByb2pJRCI6ICIxIn0=\"}");                
                        log.Info("Sync createFolder String " + strapi);
                        var apirestult = HttpHelper.PostUrl("createFolder_async", strapi);
                        log.Info("Sync createFolder Json  Return String " + apirestult);

                        //JObject apiresultJsobj = JObject.Parse(apirestult);
                        //string apibase641 = apiresultJsobj["jsonBase64"].ToString();
                        //var jsapiresults = Encoding.UTF8.GetString(Convert.FromBase64String(apibase641));
                        //log.Info("Sync createFolder return JsonString :" + jsapiresults);
                    }

                    return "1";
                }
                else
                    return "0";
                //return "";
            }
            catch (Exception ex)
            {
                log.Error("InsertProject Exception :" + ex.Message.ToString());
                return "";
            }
        }
        [HttpGet("AddMember")]
        public string AddMember(string usracc, string usrpwd, string userdept)
        {
            try
            {
                log.Info("AddMember 建立User 名稱:" + usracc);
                log.Info("AddMember 單位:" + userdept);


                var prochtlist = mydbhelper.SelectMemberAcc(usracc);
                log.Info("project name 重複筆數 :" + prochtlist.Count.ToString());
                if (prochtlist.Count > 0)
                {
                    return "-5";
                }

                //base64
                string base64pwd = "";
                byte[] bytepwd = Encoding.GetEncoding("utf-8").GetBytes(usrpwd);

                //參數編成 Base64 字串
                base64pwd = Convert.ToBase64String(bytepwd);
                var pwdmd5 = MD5Str.MD5(usrpwd);
                string insertsql = "insert into T_Member(useraccount,username,password,dept_id,isAdmin,createtime)values('" + usracc + "','" + usracc + "','" + pwdmd5 + "','" + userdept + "',0,Now());";
                var result = mydbhelper.InsertDB(insertsql);
                if (result)
                {


                    return "1";
                }
                else
                    return "0";
                //return "";
            }
            catch (Exception ex)
            {
                log.Error("InsertProject Exception :" + ex.Message.ToString());
                return "";
            }
        }

        [HttpGet("UpdateProjectStatus")]
        public string UpdateProjectStatus(string pname, int project_status)
        {
            //string insertsql = "insert into T_Member(project_name,project_desc,project_path,exoprt_path,projectowner_id,createtime)values('" + pname + "','" + prodesc + "','" + pinput + "','" + poutput + "'," + powner + ",Now());";
            //var result = mydbhelper.InsertProject(insertsql);
            return "";
        }

        [HttpGet("CancelProjectStatus")]
        public string CancelProjectStatus(int project_id, string pname, int project_status)
        {
            ////string insertsql = "insert into T_Member(project_name,project_desc,project_path,exoprt_path,projectowner_id,createtime)values('" + pname + "','" + prodesc + "','" + pinput + "','" + poutput + "'," + powner + ",Now());";
            // result = mydbhelper.InsertProject(insertsql);
            log.Info("取消專案 ");
            log.Info("取消專案 ID:" + project_id.ToString());
            log.Info("取消專案 名稱:" + pname);
            mydbhelper.UpdateProjectStatus(project_id, project_status);
            mydbhelper.CancelProjectDeleteData(project_id);
            return "";
        }

        [HttpGet("DeleteProject")]
        public string DeleteProject(int project_id)
        {
            log.Info("刪除專案 :" + project_id.ToString());
            ////string insertsql = "insert into T_Member(project_name,project_desc,project_path,exoprt_path,projectowner_id,createtime)values('" + pname + "','" + prodesc + "','" + pinput + "','" + poutput + "'," + powner + ",Now());";
            // result = mydbhelper.InsertProject(insertsql);
            mydbhelper.DeleteProject(project_id);
            log.Info("刪除專案 成功");
            return "True";
        }

        [HttpGet("delDept")]
        public int delDept(int depid)
        {
            log.Info("刪除單位 :" + depid.ToString());
            int isdel = 0;
            ////string insertsql = "insert into T_Member(project_name,project_desc,project_path,exoprt_path,projectowner_id,createtime)values('" + pname + "','" + prodesc + "','" + pinput + "','" + poutput + "'," + powner + ",Now());";
            // result = mydbhelper.InsertProject(insertsql);
            try
            {
                var lstmember = mydbhelper.selectdeptbymember(depid);
                if (lstmember.Count == 0)
                {
                    isdel = -1;
                }
                else
                {
                    mydbhelper.DeleteDept(depid);
                    log.Info("刪除專案 成功");
                    isdel = 1;
                }
            }
            catch (Exception ex)
            {
                log.Error("刪除專案 Exception :" + ex.Message.ToString());
                isdel = -99;
            }
            return isdel;
        }


        [HttpGet("delUser")]
        public bool delUser(int usrid)
        {
            log.Info("刪除使用者ID :" + usrid.ToString());
            bool isdel = false;
            ////string insertsql = "insert into T_Member(project_name,project_desc,project_path,exoprt_path,projectowner_id,createtime)values('" + pname + "','" + prodesc + "','" + pinput + "','" + poutput + "'," + powner + ",Now());";
            // result = mydbhelper.InsertProject(insertsql);
            try
            {
                mydbhelper.DeleteUser(usrid);
                log.Info("刪除User 成功");
            }
            catch (Exception ex)
            {
                log.Error("刪除User Exception :" + ex.Message.ToString());
            }
            return isdel;
        }



        [HttpGet("returnMLStatus")]
        public bool returnMLStatus(string pid, string pname, string jobname)
        {
            log.Info("returnMLStatus");
            log.Info("pid :" + pid);
            bool restatus = false;
            try
            {
                string projstep = "returnMLStatus";
                mydbhelper.CancelMLData(int.Parse(pid));
                var prostatus = mydbhelper.UpdateProjectStauts(int.Parse(pid), 6, "感興趣欄位選擇");
                restatus = true;
            }
            catch (Exception ex)
            {
                log.Error("returnMLStatus exception :" + ex.Message);
            }

            return restatus;
        }



        public class ProjectStatusInputModel
        {
            public int dp_project_id { get; set; }
            public string project_name { get; set; }
            public string file_name { get; set; }
            public string aes_col { get; set; }
        }

        [HttpGet("dp_report")]
        public IActionResult dp_report([FromQuery] ProjectStatusInputModel inputModel)
        {
            log.Info("dp_report 查詢報表 WebAPI");

            int project_id = inputModel.dp_project_id;
            string jsonString = "";
            var responseList = new List<object>();
            var raw_info = new List<Rawdata_info>();
            var syn_info = new List<Syndata_info>();
            var ep = 0.0;
            try
            {
                var lstST = proj_Service.SelectProjSample5TB(project_id.ToString());
                if (lstST.Count > 0)
                {
                    string psStatus = "";
                    foreach (var item in lstST)
                    {
                        ep = item.epsilon;
                    }

                  // ViewData["ep"] = ep;
                }

                var tab_fname = mydbhelper.SelectProUtilityResultCount(project_id);
                if (tab_fname != null)
                {
                    if (tab_fname.Count > 0)
                    {
                        foreach (var item in tab_fname)
                        {
                            var str_target_col = item.target_col;
                            ViewData["target_col"] = str_target_col;

                            var lstutility = mydbhelper.SelectProUtilityResult(project_id, item.target_col, "statistic");
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
                                        if (raw_type == "category")
                                        {
                                            var typevalue = "類別型";
                                            JObject raw_value_attr = JObject.Parse(raw_col_attr["value"].ToString());
                                            var value_attr = raw_value_attr.ToString();
                                            // 将 JSON 字符串解析为 Dictionary<string, int>
                                            Dictionary<string, int> valueDict = JsonConvert.DeserializeObject<Dictionary<string, int>>(value_attr);
                                            List<Dictionary<string, object>> rawcolValueList = new List<Dictionary<string, object>>();

                                            // 输出键和值
                                            foreach (var kvp in valueDict)
                                            {
                                                var category = new Dictionary<string, object>
                                                {
                                                    { "col_value", kvp.Key },
                                                    { "col_count", kvp.Value }
                                                };

                                                rawcolValueList.Add(category);
                                            }
                                            string colValueJson = JsonConvert.SerializeObject(rawcolValueList);
                                            // raw_newhtml += String.Format(utility_html, target_col_str[i], typevalue, value_content);
                                            var jsonObject = new Rawdata_info
                                            {
                                                col_name = target_col_str[i],
                                                col_type = typevalue,
                                                col_value = rawcolValueList

                                            };

                                            raw_info.Add(jsonObject);

                                            JObject syn_value_attr = JObject.Parse(syn_col_attr["value"].ToString());
                                            var value_attr_syn = syn_value_attr.ToString();
                                            // 将 JSON 字符串解析为 Dictionary<string, int>
                                            Dictionary<string, int> syn_valueDict = JsonConvert.DeserializeObject<Dictionary<string, int>>(value_attr_syn);
                                            value_content = "";
                                            // 输出键和值
                                            List<Dictionary<string, object>> syncolValueList = new List<Dictionary<string, object>>();

                                            // 输出键和值
                                            foreach (var kvp in syn_valueDict)
                                            {
                                                var category = new Dictionary<string, object>
                                                {
                                                    { "col_value", kvp.Key },
                                                    { "col_count", kvp.Value }
                                                };

                                                syncolValueList.Add(category);
                                            }
                                            string syncolValueJson = JsonConvert.SerializeObject(syncolValueList);

                                            var synObject = new Syndata_info
                                            {
                                                col_name = target_col_str[i],
                                                col_type = typevalue,
                                                col_value = syncolValueList

                                            };

                                            syn_info.Add(synObject);
                                        }
                                        else
                                        {
                                            JObject raw_value_attr = JObject.Parse(raw_col_attr["value"].ToString());
                                            var value_attr = raw_value_attr.ToString();
                                            var typevalue = "數值型";
                                            // 将 JSON 字符串解析为 Dictionary<string, int>
                                            Dictionary<string, double> valueDict = JsonConvert.DeserializeObject<Dictionary<string, double>>(value_attr);
                                            ColValue col_value = null;
                                            // 输出键和值
                                            foreach (var kvp in valueDict)
                                            {

                                                col_value = new ColValue
                                                {
                                                    Min = Convert.ToDouble(valueDict["min"]),
                                                    Max = Convert.ToDouble(valueDict["max"]),
                                                    Mean = Convert.ToDouble(valueDict["mean"]),
                                                    Median = Convert.ToDouble(valueDict["median"]),
                                                    Std = Convert.ToDouble(valueDict["std"])
                                                };

                                            }
                                            Rawdata_info rawdataInfo = new Rawdata_info
                                            {
                                                col_name = target_col_str[i], // 設定欄位名稱
                                                col_type = typevalue, // 設定欄位型別
                                                col_value = col_value
                                            };
                                            raw_info.Add(rawdataInfo);
                                            JObject syn_value_attr = JObject.Parse(syn_col_attr["value"].ToString());
                                            var value_attr_syn = syn_value_attr.ToString();
                                            // 将 JSON 字符串解析为 Dictionary<string, int>
                                            Dictionary<string, double> syn_valueDict = JsonConvert.DeserializeObject<Dictionary<string, double>>(value_attr_syn);
                                            value_content = "";
                                            // 输出键和值
                                            ColValue syn_col_value = null;
                                            foreach (var kvp in syn_valueDict)
                                            {

                                                syn_col_value = new ColValue
                                                {
                                                    Min = Convert.ToDouble(syn_valueDict["min"]),
                                                    Max = Convert.ToDouble(syn_valueDict["max"]),
                                                    Mean = Convert.ToDouble(syn_valueDict["mean"]),
                                                    Median = Convert.ToDouble(syn_valueDict["median"]),
                                                    Std = Convert.ToDouble(syn_valueDict["std"])

                                                };


                                            }

                                            Syndata_info syndataInfo = new Syndata_info
                                            {
                                                col_name = target_col_str[i], // 設定欄位名稱
                                                col_type = typevalue, // 設定欄位型別
                                                col_value = syn_col_value
                                            };
                                            syn_info.Add(syndataInfo);

                                        }

                                    }
                                }
                            }
                        }


                        //Report
                        var ganreport = new gan_report
                        {
                            epsilon = (int)ep,
                            rawdata_info = raw_info,
                            syndata_info = syn_info

                        };

                        responseList.Add(ganreport);
                    }
                    else
                    {
                        var nullObject = new
                        {
                            status = -1,
                            msg = "project is not finish",
                            obj = new
                            {

                            }
                        };

                        // 将匿名对象转换为 JSON 字符串
                        jsonString = JsonConvert.SerializeObject(nullObject);
                        responseList.Add(nullObject);
                    }
                }
                else
                {
                    var nullObject = new
                    {
                        status = -1,
                        msg = "project is null",
                        obj = new
                        {

                        }
                    };

                    // 将匿名对象转换为 JSON 字符串
                    jsonString = JsonConvert.SerializeObject(nullObject);
                    responseList.Add(nullObject);
                }
            }
            catch (Exception ex)
            {
                string errormsg = ex.Message;
                log.Error("syn_report Exception : " + errormsg);
                return BadRequest(new { status = -2, msg = errormsg });
            }
            return Json(responseList);
        }


        [HttpGet("dp_report_1")]
        public IActionResult dp_report_1([FromQuery] ProjectStatusInputModel inputModel)
        {
            log.Info("dp_report 查詢報表 WebAPI");

            int project_id = inputModel.dp_project_id;
            string jsonString = "";
            var responseList = new List<object>();
            var raw_info = new List<Rawdata_info>();
            var dp_info = new List<Syndata_info>();

            try
            {
                var tab_fname = mydbhelper.SelectProUtilityResultCount(project_id);
                if (tab_fname != null)
                {
                    if (tab_fname.Count > 0)
                    {
                        foreach (var item in tab_fname)
                        {
                            var str_target_col = item.target_col;
                            ViewData["target_col"] = str_target_col;

                            var lstutility = mydbhelper.SelectProUtilityResult(project_id, item.target_col, "statistic");
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
                                    string dp_data = apidecode["syn. data"].ToString();
                                    JObject raw_str = JObject.Parse(raw_data);
                                    JObject dp_str = JObject.Parse(dp_data);
                                    for (int i = 0; i < target_col_str.Count(); i++)
                                    {
                                        var target_raw_data = raw_str[target_col_str[i]].ToString();
                                        var target_dp_data = dp_str[target_col_str[i]].ToString();
                                        JObject raw_col_attr = JObject.Parse(target_raw_data);
                                        JObject dp_col_attr = JObject.Parse(target_dp_data);
                                        var raw_type = raw_col_attr["type"].ToString();
                                        var dp_type = dp_col_attr["type"].ToString();
                                        var value_content = "";
                                        if (raw_type == "category")
                                        {
                                            var typevalue = "類別型";
                                            JObject raw_value_attr = JObject.Parse(raw_col_attr["value"].ToString());
                                            var value_attr = raw_value_attr.ToString();
                                            // 将 JSON 字符串解析为 Dictionary<string, int>
                                            Dictionary<string, int> valueDict = JsonConvert.DeserializeObject<Dictionary<string, int>>(value_attr);
                                            List<Dictionary<string, object>> rawcolValueList = new List<Dictionary<string, object>>();

                                            // 输出键和值
                                            foreach (var kvp in valueDict)
                                            {
                                                var category = new Dictionary<string, object>
                                                {
                                                    { "col_value", kvp.Key },
                                                    { "col_count", kvp.Value }
                                                };

                                                rawcolValueList.Add(category);
                                            }
                                            string colValueJson = JsonConvert.SerializeObject(rawcolValueList);
                                            // raw_newhtml += String.Format(utility_html, target_col_str[i], typevalue, value_content);
                                            var jsonObject = new Rawdata_info
                                            {
                                                col_name = target_col_str[i],
                                                col_type = typevalue,
                                                col_value = rawcolValueList

                                            };

                                            raw_info.Add(jsonObject);

                                            JObject dp_value_attr = JObject.Parse(dp_col_attr["value"].ToString());
                                            var value_attr_syn = dp_value_attr.ToString();
                                            // 将 JSON 字符串解析为 Dictionary<string, int>
                                            Dictionary<string, int> dp_valueDict = JsonConvert.DeserializeObject<Dictionary<string, int>>(value_attr_syn);
                                            value_content = "";
                                            // 输出键和值
                                            List<Dictionary<string, object>> syncolValueList = new List<Dictionary<string, object>>();

                                            // 输出键和值
                                            foreach (var kvp in valueDict)
                                            {
                                                var category = new Dictionary<string, object>
                                                {
                                                    { "col_value", kvp.Key },
                                                    { "col_count", kvp.Value }
                                                };

                                                syncolValueList.Add(category);
                                            }
                                            string syncolValueJson = JsonConvert.SerializeObject(syncolValueList);

                                            var synObject = new Syndata_info
                                            {
                                                col_name = target_col_str[i],
                                                col_type = typevalue,
                                                col_value = syncolValueList

                                            };

                                            dp_info.Add(synObject);
                                        }
                                        else
                                        {
                                            JObject raw_value_attr = JObject.Parse(raw_col_attr["value"].ToString());
                                            var value_attr = raw_value_attr.ToString();
                                            var typevalue = "數值型";
                                            // 将 JSON 字符串解析为 Dictionary<string, int>
                                            Dictionary<string, double> valueDict = JsonConvert.DeserializeObject<Dictionary<string, double>>(value_attr);
                                            ColValue col_value = null;
                                            // 输出键和值
                                            foreach (var kvp in valueDict)
                                            {

                                                col_value = new ColValue
                                                {
                                                    Min = Convert.ToDouble(valueDict["min"]),
                                                    Max = Convert.ToDouble(valueDict["max"]),
                                                    Mean = Convert.ToDouble(valueDict["mean"]),
                                                    Median = Convert.ToDouble(valueDict["median"]),
                                                    Std = Convert.ToDouble(valueDict["std"])
                                                };

                                            }
                                            Rawdata_info rawdataInfo = new Rawdata_info
                                            {
                                                col_name = target_col_str[i], // 設定欄位名稱
                                                col_type = typevalue, // 設定欄位型別
                                                col_value = col_value
                                            };
                                            raw_info.Add(rawdataInfo);
                                            JObject dp_value_attr = JObject.Parse(dp_col_attr["value"].ToString());
                                            var value_attr_syn = dp_value_attr.ToString();
                                            // 将 JSON 字符串解析为 Dictionary<string, int>
                                            Dictionary<string, double> dp_valueDict = JsonConvert.DeserializeObject<Dictionary<string, double>>(value_attr_syn);
                                            value_content = "";
                                            // 输出键和值
                                            ColValue dp_col_value = null;
                                            foreach (var kvp in dp_valueDict)
                                            {

                                                dp_col_value = new ColValue
                                                {
                                                    Min = Convert.ToDouble(valueDict["min"]),
                                                    Max = Convert.ToDouble(valueDict["max"]),
                                                    Mean = Convert.ToDouble(valueDict["mean"]),
                                                    Median = Convert.ToDouble(valueDict["median"]),
                                                    Std = Convert.ToDouble(valueDict["std"])

                                                };


                                            }

                                            Syndata_info syndataInfo = new Syndata_info
                                            {
                                                col_name = target_col_str[i], // 設定欄位名稱
                                                col_type = typevalue, // 設定欄位型別
                                                col_value = dp_col_value
                                            };
                                            dp_info.Add(syndataInfo);

                                        }

                                    }
                                }
                            }
                        }


                        //Report
                        var ganreport = new gan_report
                        {
                            rawdata_info = raw_info,
                            syndata_info = dp_info

                        };

                        responseList.Add(ganreport);
                    }
                    else
                    {
                        var nullObject = new
                        {
                            status = -1,
                            msg = "project is not finish",
                            obj = new
                            {

                            }
                        };

                        // 将匿名对象转换为 JSON 字符串
                        jsonString = JsonConvert.SerializeObject(nullObject);
                        responseList.Add(nullObject);
                    }
                }
                else
                {
                    var nullObject = new
                    {
                        status = -1,
                        msg = "project is null",
                        obj = new
                        {

                        }
                    };

                    // 将匿名对象转换为 JSON 字符串
                    jsonString = JsonConvert.SerializeObject(nullObject);
                    responseList.Add(nullObject);
                }
            }
            catch (Exception ex)
            {
                string errormsg = ex.Message;
                log.Error("dp_report Exception : " + errormsg);
                return BadRequest(new { status = -2, msg = errormsg });
            }
            return Json(responseList);
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


        [HttpGet("dp_reset")]
        ///
        //public IActionResult k_checkstatus(string project_name)
        public IActionResult dp_reset([FromQuery] ProjectStatusInputModel inputModel)
        {
            log.Info("dp_reset 重設專案 WebAPI");
            //string projectName = inputModel.project_name;
            int project_id = inputModel.dp_project_id;
            log.Info("project_id :" + project_id.ToString());
            log.Info("取消專案 ");
            var responseList = new List<object>();
            //log.Info("取消專案 ID:" + project_id.ToString());
            //log.Info("取消專案 名稱:" + pname);
            try
            {
                mydbhelper.UpdateProjectStatus(project_id, 2);
                mydbhelper.CancelProjectDeleteData(project_id);
                string jsonString = "";


                var nullObject = new
                {
                    status = 1,
                    msg = "update success",
                    obj = new
                    {

                    }
                };

                // 将匿名对象转换为 JSON 字符串
                jsonString = JsonConvert.SerializeObject(nullObject);
                responseList.Add(nullObject);
            }
            catch (Exception ex)
            {
                string errormsg = ex.Message;
                log.Error("dp_reset Exception : " + errormsg);
                return BadRequest(new { status = -1, msg = errormsg });
            }
            return Json(responseList);
        }


        [HttpGet("dp_checkstatus")]
        ///
        //public IActionResult k_checkstatus(string project_name)
        public IActionResult dp_checkstatus([FromQuery] ProjectStatusInputModel inputModel)
        {
            log.Info("dp_checkstatus 查詢狀態 WebAPI");
            string projectName = inputModel.project_name;
            log.Info("project_name :" + projectName);
            string jsonString = "";
            int project_id = 0;
            //project_name
            var responseList = new List<object>();
            try
            {
                if (projectName == null)
                {
                    var nullObject = new
                    {
                        status = -1,
                        msg = "project_name is null",
                        obj = new
                        {

                        }
                    };

                    // 将匿名对象转换为 JSON 字符串
                    jsonString = JsonConvert.SerializeObject(nullObject);
                    responseList.Add(nullObject);
                }
                else
                {
                    //查詢專案名稱是否有在資料庫
                    var lstproject = mydbhelper.CheckProjectStatus(projectName);
                    string statusname = "";
                    string return_url = _configuration["Dp_WebAPI:URL"];
                    //string return_url = "https://www.data-privacy.com.tw/diffapi";
                    int proj_status = 0;
                    //int project_id = 0;
                    string downloadpath = "";
                    if (lstproject != null)
                    {
                        if (lstproject.Count > 0)
                        {
                            foreach (var item in lstproject)
                            {
                                proj_status = item.project_status;
                              
                                project_id = item.Project_id;
                              
                                
                               
                            }

                            var lst = mydbhelper.getDP_DownloadPath(project_id.ToString());
                            foreach(var item in lst)
                            {
                                downloadpath = item.downloadpath;
                            }
                            switch (proj_status)
                            {
                                case 0:
                                    statusname = "新建專案";
                                    return_url += "/ProjectStep/Preview?proj_id=" + WebUtility.UrlEncode(project_id.ToString()) + "&project_name=" + WebUtility.UrlEncode(projectName) + "&stepstatus=" + WebUtility.UrlEncode(proj_status.ToString());
                                    break;

                                case 1:
                                    statusname = "資料匯入中";
                                    return_url = "";
                                    break;
                                case 2:
                                    statusname = "資料欄位設定";
                                    return_url += "/ProjectStep/DpSync?proj_id=" + WebUtility.UrlEncode(project_id.ToString()) + "&project_name=" + WebUtility.UrlEncode(projectName) + "&stepstatus=" + WebUtility.UrlEncode(proj_status.ToString());

                                    break;
                                case 3:
                                    statusname = "關聯欄位";
                                    return_url += "/ProjectStep/Dataassociation?proj_id=" + WebUtility.UrlEncode(project_id.ToString()) + "&project_name=" + WebUtility.UrlEncode(projectName) + "&stepstatus=" + WebUtility.UrlEncode(proj_status.ToString());
                                    break;
                                case 4:
                                    statusname = "差分隱私處理";
                                    return_url += "/ProjectStep/MLutility?proj_id=" + WebUtility.UrlEncode(project_id.ToString()) + "&project_name=" + WebUtility.UrlEncode(projectName) + "&stepstatus=" + WebUtility.UrlEncode(proj_status.ToString());

                                    break;
                                case 41:
                                    statusname = "差分隱私處理";
                                    return_url += "/ProjectStep/MLutility?proj_id=" + WebUtility.UrlEncode(project_id.ToString()) + "&project_name=" + WebUtility.UrlEncode(projectName) + "&stepstatus=" + WebUtility.UrlEncode(proj_status.ToString());
                                    proj_status = 4;
                                    break;
                                case 42:
                                    statusname = "差分隱私處理";
                                    return_url += "/ProjectStep/MLutility?proj_id=" + WebUtility.UrlEncode(project_id.ToString()) + "&project_name=" + WebUtility.UrlEncode(projectName) + "&stepstatus=" + WebUtility.UrlEncode(proj_status.ToString());
                                    proj_status = 4;

                                    break;
                                case 43:
                                    statusname = "差分隱私處理";
                                    return_url += "/ProjectStep/MLutility?proj_id=" + WebUtility.UrlEncode(project_id.ToString()) + "&project_name=" + WebUtility.UrlEncode(projectName) + "&stepstatus=" + WebUtility.UrlEncode(proj_status.ToString());
                                    proj_status = 4;

                                    break;
                                case 5:
                                    statusname = "差分隱私處理中";
                                     return_url = "";
                                  //  return_url += "/ProjectStep/MLutility?proj_id=" + WebUtility.UrlEncode(project_id.ToString()) + "&project_name=" + WebUtility.UrlEncode(projectName) + "&stepstatus=" + WebUtility.UrlEncode(proj_status.ToString());

                                    break;
                                case 6:
                                    statusname = "資料相似度比對";
                                    return_url += "/ProjectStep/DataCheck?proj_id=" + WebUtility.UrlEncode(project_id.ToString()) + "&project_name=" + WebUtility.UrlEncode(projectName) + "&stepstatus=" + WebUtility.UrlEncode(proj_status.ToString());
                                    break;
                                case 7:
                                    statusname = "資料相似度比對處理中";
                                     return_url = "";
                                    //return_url += "/ProjectStep/DpSyncReport?proj_id=" + WebUtility.UrlEncode(project_id.ToString()) + "&project_name=" + WebUtility.UrlEncode(projectName) + "&stepstatus=" + WebUtility.UrlEncode(proj_status.ToString());
                                    break;
                                case 8:
                                    statusname = "查看報表";
                                    return_url += "/ProjectStep/New_DpSyncReport?proj_id=" + WebUtility.UrlEncode(project_id.ToString()) + "&project_name=" + WebUtility.UrlEncode(projectName) + "&stepstatus=" + WebUtility.UrlEncode(proj_status.ToString());
                                    //downloadpath = "";
                                    break;
                            

                                case 9:
                                    statusname = "資料下載";
                                    return_url += "/ProjectStep/New_DpSyncReport?proj_id=" + WebUtility.UrlEncode(project_id.ToString()) + "&project_name=" + WebUtility.UrlEncode(projectName) + "&stepstatus=" + WebUtility.UrlEncode(proj_status.ToString());
                                    //downloadpath = "";
                                    break;
                                case 99:
                                    statusname = "資料差分隱私錯誤";
                                    return_url += "/ProjectStep/DpSync?proj_id=" + WebUtility.UrlEncode(project_id.ToString()) + "&project_name=" + WebUtility.UrlEncode(projectName) + "&stepstatus=" + WebUtility.UrlEncode(proj_status.ToString());
                                    //downloadpath = "";
                                    break;
                                case 98:
                                    statusname = "資料可用性錯誤";
                                    return_url += "/ProjectStep/MLutility?proj_id=" + WebUtility.UrlEncode(project_id.ToString()) + "&project_name=" + WebUtility.UrlEncode(projectName) + "&stepstatus=" + WebUtility.UrlEncode(proj_status.ToString());
                                   // downloadpath = "";
                                    break;
                            }
                            var responseObject = new
                            {
                                status = 1,
                                msg = "",
                                obj = new
                                {
                                    project_id = project_id,
                                    project_status = proj_status,
                                    status_name = statusname,
                                    return_url = return_url,
                                    downloadpath = downloadpath
                                }
                            };

                            // 将匿名对象转换为 JSON 字符串
                            jsonString = JsonConvert.SerializeObject(responseObject);
                            log.Info("check gan status :" + jsonString);
                            responseList.Add(responseObject);
                        }
                        else
                        {
                            var nullObject = new
                            {
                                status = 0,
                                msg = "project_name 並不存在",
                                obj = new
                                {

                                }
                            };

                            // 将匿名对象转换为 JSON 字符串
                            jsonString = JsonConvert.SerializeObject(nullObject);
                            responseList.Add(nullObject);
                        }
                    }
                    else
                    {
                        var nullObject = new
                        {
                            status = 0,
                            msg = "project_name 並不存在",
                            obj = new
                            {

                            }
                        };

                        // 将匿名对象转换为 JSON 字符串
                        jsonString = JsonConvert.SerializeObject(nullObject);
                        responseList.Add(nullObject);
                    }
                }
            }
            catch (Exception ex)
            {
                string errormsg = ex.Message;
                log.Error("gan_checkstatus Exception : " + errormsg);
                return BadRequest(new { status = -1, msg = errormsg });
            }
            return Json(responseList);
        }



        [HttpGet("dp_conn")]
        ///
        //public IActionResult k_checkstatus(string project_name)
        public IActionResult dp_conn([FromQuery] ProjectStatusInputModel inputModel)
        {
            log.Info("dp_conn 串接子系統");
            string projectName = inputModel.project_name;
            string filename = inputModel.file_name;
            var responseList = new List<object>();

            try
            {
                string sql = "select * from T_Project where project_name='" + projectName + "'";
                log.Info("WebAPI InsertProject Sql :" + sql);
                var prolist = mydbhelper.SelectProject(sql);
                log.Info("project name 重複筆數 :" + prolist.Count.ToString());
                if (prolist.Count > 0)
                {
                    var mutiproj = new
                    {
                        status = -1,
                        msg = "Muti Project in K ",
                        obj = new
                        {

                        }
                    };

                    //var jsonString = JsonConvert.SerializeObject(mutiproj);
                    responseList.Add(mutiproj);
                }
                else
                {

                    string insertsql = "insert into T_Project(project_name,project_desc,project_path,export_path,projectowner_id,createtime,project_cht)values('" + projectName + "','" + projectName + "','" + projectName + "','" + projectName + "'," + "1" + ",Now(),'" + projectName + "');";
                    var result = mydbhelper.InsertDB(insertsql);
                    bool createfolder = false;
                    string project_id = "";
                    if (result)
                    {
                        var proId = mydbhelper.SelectProject(sql);


                        foreach (var item in proId)
                        {
                            project_id = item.Project_id.ToString();
                        }
                        //createfolder
                        var jsoncreatefolder = "";
                        createFolderAPI cfolder = new createFolderAPI
                        {
                            userID = "1",
                            projID = project_id,
                            //serverfolder.projName = "test_import_all";
                            projName = projectName
                        };
                        string serverfolderstr = JsonHelper.SerializeObject(cfolder);
                        log.Info("Sync createFolder Json String :" + serverfolderstr);
                        //string pythonstr = "{\"projName\": \"test_import_all\", \"projStep\": \"getServerFolder\", \"projID\": \"1\"}";
                        //byte[] byteServer = Encoding.GetEncoding("utf-8").GetBytes(pythonstr);
                        byte[] byteServer = Encoding.GetEncoding("utf-8").GetBytes(serverfolderstr);

                        //參數編成 Base64 字串
                        string JsonServer = Convert.ToBase64String(byteServer);

                        APIModel apiModel = new APIModel
                        {
                            jsonBase64 = JsonServer
                        };

                        string strapi = JsonHelper.SerializeObject(apiModel);
                        //var apirestult=HttpHelper.PostUrl("getServerFolder", "{\"jsonBase64\":\"eyJwcm9qTmFtZSI6ICJ0ZXN0X2ltcG9ydF9hbGwiLCAicHJvalN0ZXAiOiAiZ2V0U2VydmVyRm9sZGVyIiwgInByb2pJRCI6ICIxIn0=\"}");                
                        log.Info("Sync createFolder String " + strapi);
                        var apirestult = HttpHelper.PostUrl("createFolder_async", strapi);
                        log.Info("Sync createFolder Json  Return String " + apirestult);
                        JObject apiresultJsobj = JObject.Parse(apirestult);
                        string createfolder_STATE = apiresultJsobj["STATE"].ToString();
                        if (createfolder_STATE == "SUCCESS")
                        {
                            createfolder = true;
                        }
                        else
                        {
                            mydbhelper.DeleteProject(int.Parse(project_id));
                            var mutiproj = new
                            {
                                status = -2,
                                msg = "Create Folder Error",
                                obj = new
                                {

                                }
                            };

                            //var jsonString = JsonConvert.SerializeObject(mutiproj);
                            responseList.Add(mutiproj);
                        }
                    }

                    if (createfolder)
                    {
                        var proId = mydbhelper.SelectProject(sql);
                        foreach (var item in proId)
                        {
                            log.Info("WebAPI InsertProject Insert ProjectStatus ");

                            //var prostatussql = "insert into T_ProjectStatus(project_id,project_status,statusname,createtime)values(" + item.Project_id + ",0,'資料匯入處理中',now())";
                            var psresult = projService.InsertProjectStauts(item.Project_id, 0, "資料專案開啟");

                            //insert專案成功 匯入資料 
                            previewDataModelAPI previewData = new previewDataModelAPI
                            {
                                userID = "1",
                                projID = item.Project_id.ToString(),
                                projName = projectName,
                                //serverfolder.projName = "test_import_all";
                                fileName = filename,

                            };
                            string serverfolderstr = JsonHelper.SerializeObject(previewData);
                            log.Info("PreviewDatra Json String :" + serverfolderstr);

                            // string pythonstr = "{\"projName\": \"test_import_all\", \"projStep\": \"getServerFolder\", \"projID\": \"1\"}";
                            byte[] byteServer = Encoding.GetEncoding("utf-8").GetBytes(serverfolderstr);

                            //參數編成 Base64 字串
                            string JsonServer = Convert.ToBase64String(byteServer);

                            APIModel apiModel = new APIModel
                            {
                                jsonBase64 = JsonServer
                            };

                            string strapi = JsonHelper.SerializeObject(apiModel);
                            //var apirestult=HttpHelper.PostUrl("getServerFolder", "{\"jsonBase64\":\"eyJwcm9qTmFtZSI6ICJ0ZXN0X2ltcG9ydF9hbGwiLCAicHJvalN0ZXAiOiAiZ2V0U2VydmVyRm9sZGVyIiwgInByb2pJRCI6ICIxIn0=\"}");                
                            log.Info("Import File Json String " + strapi);
                            var apirestult = HttpHelper.PostUrl("PETs_preview_async", strapi);
                            //var apirestult = await httphelper.PostUrl_async("ImportFile", strapi);

                            log.Info("Import File Json  Return String " + apirestult);
                            if (apirestult != "")
                            {
                                // JObject apiresultJsobj = JObject.Parse(apirestult);
                                //string apibase641 = apiresultJsobj["jsonBase64"].ToString();
                                //var jsapiresults = Encoding.UTF8.GetString(Convert.FromBase64String(apibase641));
                                //log.Info("ImportFile return JsonString :" + jsapiresults);
                                JObject apidecode = JObject.Parse(apirestult);
                                string state = apidecode["STATE"].ToString();
                                if (state == "FAIL")
                                {

                                    string errmsg = apidecode["ERRMSG"].ToString();
                                    log.Error("preview_async State Error :" + state);
                                    mydbhelper.DeleteProject(int.Parse(project_id));
                                    var mutiproj = new
                                    {
                                        status = -2,
                                        msg = "errmsg",
                                        obj = new
                                        {

                                        }
                                    };
                                    //return "-1";
                                }
                                else
                                {

                                    //更新系統狀態
                                    var prostatus = mydbhelper.UpdateProjectStauts(item.Project_id, 1, "資料匯入中");
                                    if (prostatus)
                                    {

                                        var mutiproj = new
                                        {
                                            status = 1,
                                            msg = "資料匯入中",
                                            obj = new
                                            {

                                            }
                                        };

                                        //var jsonString = JsonConvert.SerializeObject(mutiproj);
                                        responseList.Add(mutiproj);
                                    }

                                }
                            }
                            else
                            {
                                log.Error("ImportFile Return Json Error : Session Timeout");
                                var mutiproj = new
                                {
                                    status = -2,
                                    msg = "System Timeout",
                                    obj = new
                                    {

                                    }
                                };

                                //var jsonString = JsonConvert.SerializeObject(mutiproj);
                                responseList.Add(mutiproj);
                            }
                        }

                    }
                }
            }
            catch (Exception ex)
            {
                string errormsg = ex.Message;
                log.Error("dp_conn Exception : " + errormsg);
                return BadRequest(new { status = -1, msg = errormsg });
            }
            return Json(responseList);
        }


    }
}
