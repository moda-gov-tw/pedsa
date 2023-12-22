using System;
using System.Collections.Generic;
using System.Linq;
using System.Net;
using System.Text;
using System.Threading.Tasks;
using DeIdWeb_V2_K.Filters;
using DeIdWeb_V2_K.Infrastructure.Reposiotry;
using DeIdWeb_V2_K.Infrastructure.Service;
using DeIdWeb_V2_K.Models;
using log4net;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Localization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Extensions.Configuration;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;
using Resources;

namespace DeIdWeb_V2_K.Controllers
{
    [TypeFilter(typeof(CultureFilter))]
    [Produces("application/json")]
    [Route("api/WebAPI")]
    public class WebAPIController : Controller
    {
        public Member_Service mService = new Member_Service();
        public ProjectStatus_Service psService = new ProjectStatus_Service();
        public MySqlDBHelper mydbhelper = new MySqlDBHelper();
        public ProjectStatus_Service projService = new ProjectStatus_Service();
        public ProjectSample_Service proj_Service = new ProjectSample_Service();
        public HttpHelper httphelper = new HttpHelper();
        public GetGenJsonRep genJsonRp = new GetGenJsonRep();
        private ILog log = LogManager.GetLogger(Startup.repository.Name, typeof(WebAPIController));
        private readonly ILocalizer _localizer;
        private readonly IConfiguration _configuration;
        public WebAPIController(ILocalizer localizer, IConfiguration configuration)
        {
            _localizer = localizer;
            _configuration = configuration;
        }

        // GET api/values
        /// <summary>
        /// Update 欄位設定
        /// </summary>
        /// <returns></returns>
        [HttpGet("UpdateColSetting")]
        public string UpdateColSetting(string pid, string configstring)
        {
            bool isUpdate = false;
            log.Info("UpdateColSetting API");
            //var finalstr = unmap_col + "^" + ps_id + "|" + update_col + "|" + update_colval + "|" + new_qi_col + "|" + newtablekeycol + "|" + final_gen_setting_value + "|" + k_risk + "|" + max_t + "|" + t1 + "|" + t2 + "|" + r_value;
            log.Info("UpdateColSetting API pid :" + pid);
            log.Info("UpdateColSetting API configstring :" + configstring);
            //log.Info("UpdateColSetting API setting_col_value :" + setting_col_value);
            //log.Info("UpdateColSetting API tablekey :" + tablekey);
            //log.Info("UpdateColSetting API gen_qi_settingvale :" + gen_qi_settingvale);
            if (pid == "")
            {
                return "-2";
            }
            try
            {
                //update 
                //var updatestresult = proj_Service.UpdateProjectSampleTableQI(pid, k_value, col_gentb_arr[b], tbarray[i]);
                var configlist = configstring.Split('^');
                if (configlist.Length > 1)
                {
                    if (configlist[0] == "no")
                    {
                        return "-1";
                    }
                    else
                    {
                        var tableconfiglist = configlist[1].Split('|');
                        if (tableconfiglist.Length > 0)
                        {
                            //var updatestresult = proj_Service.UpdateProjectSampleTableQI(pid, k_value, col_gentb_arr[b], tbarray[i]);
                            var lstSampleTB = proj_Service.SelectProjSampleTableByTableId(pid, tableconfiglist[0].ToString());
                            if (lstSampleTB == null)
                            {
                                return "-1";
                            }
                            else
                            {
                                var after_col_en = "";
                                foreach (var item in lstSampleTB)
                                {
                                    var tb_col_cht = item.pro_col_cht;
                                    var tb_col_en = item.pro_col_en;
                                    var tb_col_cht_arr = tb_col_cht.Split(',');
                                    var tb_col_en_arr = tb_col_en.Split(',');
                                    var after_col_cht_arr = tableconfiglist[1].Split(',');

                                    for (int i = 0; i < after_col_cht_arr.Length; i++)
                                    {
                                        for (int x = 0; x < tb_col_cht_arr.Length; x++)
                                        {
                                            if (after_col_cht_arr[i] == tb_col_cht_arr[x])
                                            {
                                                after_col_en += tb_col_en_arr[x] + ",";
                                                continue;
                                            }
                                        }
                                    }


                                }
                                //add |"+k_risk+"|"+max_t+"|"+t1+"|"+t2+"|"+r_value;
                                var updatestresult = proj_Service.UpdateProjectSampleTableConfig(tableconfiglist[0], pid, tableconfiglist[4], tableconfiglist[5], after_col_en, tableconfiglist[1], tableconfiglist[2], tableconfiglist[3], tableconfiglist[6], tableconfiglist[7], tableconfiglist[8], tableconfiglist[9], tableconfiglist[10]);
                                if (updatestresult)
                                {
                                    var prostatus = mydbhelper.UpdateProjectStauts(int.Parse(pid), 5, "概化規則預覽");
                                    return "1";
                                }
                                else
                                    return "-1";
                            }
                        }
                        else
                        {
                            return "-1";
                        }
                        // return "";
                    }
                }
                else
                {
                    return "-10";
                }
            }
            catch (Exception ex)
            {
                string errormsg = ex.Message.ToString();
                log.Error("UpdateColSetting Exception :" + errormsg);
                return "-99";
            }
            // return isUpdate;
        }

        [HttpGet("UpdateColumnMsg")]
        public bool UpdateColumnMsg(string pid, string pname, string selectvaluecol)
        {
            bool isUpdate = false;
            log.Info("UpdateColumnMsg API");
            log.Info("UpdateColumnMsg API selectvaluecol :" + selectvaluecol);
            log.Info("儲存欄位設定 :" + selectvaluecol);

            if (pid == "")
            {
                return false;
            }
            try
            {
                if (selectvaluecol != "")
                {
                    //select 資料-比對寫入
                    //< option value = "1" > 間接識別 </ option >
                    //                                     < option value = "2" > 敏感資料 </ option >
                    //                                      < option value = "3" > 直接識別 </ option >
                    //                                       < option value = "4" selected = "selected" > 不處理 </ option >
                    //                                          < option value = "0" > 不選用 </ option >
                    var tbcolarray = selectvaluecol.Split('|');
                    for (int x = 0; x < tbcolarray.Length; x++)
                    {
                        if (tbcolarray[x] != "")
                        {
                            string tbselectvalue = tbcolarray[x];
                            var tbcollst = tbcolarray[x].Split('*');
                            string tbname = tbcollst[0];
                            log.Info("資料集名稱 :" + tbname);
                            string tbcols = tbcollst[1];
                            var final_gen_setting_value = "";
                            var colarray = tbcols.Split(',');
                            var lstSampleTB = proj_Service.SelectProjSampleTable(pid, tbname);
                            if (lstSampleTB.Count > 0)
                            {
                                string chose_col_cht = "";
                                string chose_col_en = "";
                                string chose_col_qi = "";
                                string chose_col_value = "";
                                // string chose_col_value = "";
                                string tablekey = "";
                                foreach (var item in lstSampleTB)
                                {
                                    chose_col_cht = "";
                                    chose_col_en = "";
                                    chose_col_qi = "";
                                    chose_col_value = "";
                                    // string chose_col_value = "";
                                    tablekey = "";
                                    var col_cht = item.pro_col_cht;
                                    var col_en = item.pro_col_en;
                                    var col_cht_array = col_cht.Split(',');
                                    var col_en_array = col_en.Split(',');
                                    var before_qi_col = item.qi_col;
                                    var before_gen_setting = item.gen_qi_settingvalue;
                                    for (int i = 0; i < colarray.Length; i++)
                                    {
                                        switch (colarray[i].ToString())
                                        {
                                            case "0": //不選用
                                                break;
                                            case "1": //間接
                                                log.Info("間接識別欄位 :" + col_cht_array[i].ToString());

                                                chose_col_cht += col_cht_array[i].ToString() + ",";
                                                chose_col_qi += col_cht_array[i].ToString() + "-1" + ",";
                                                chose_col_en += col_en_array[i].ToString() + ",";
                                                chose_col_value += colarray[i].ToString() + ",";
                                                break;
                                            case "2": //敏感
                                                log.Info("敏感欄位 :" + col_cht_array[i].ToString());
                                                chose_col_cht += col_cht_array[i].ToString() + ",";
                                                chose_col_qi += col_cht_array[i].ToString() + "-2" + ",";
                                                chose_col_en += col_en_array[i].ToString() + ",";
                                                chose_col_value += colarray[i].ToString() + ",";
                                                break;
                                            case "3": // 直接
                                                chose_col_cht += col_cht_array[i].ToString() + ",";
                                                tablekey += col_cht_array[i].ToString() + ",";
                                                chose_col_en += col_en_array[i].ToString() + ",";
                                                chose_col_value += colarray[i].ToString() + ",";
                                                break;
                                            case "4": //不處理
                                                chose_col_cht += col_cht_array[i].ToString() + ",";
                                                //chose_col_qi += col_cht_array[i].ToString() + ",";
                                                chose_col_en += col_en_array[i].ToString() + ",";
                                                chose_col_value += colarray[i].ToString() + ",";
                                                break;
                                        }
                                    }
                                    if (chose_col_cht.Length > 1)
                                    {
                                        chose_col_cht = chose_col_cht.Substring(0, chose_col_cht.Length - 1);
                                    }
                                    if (chose_col_en.Length > 1)
                                    {
                                        chose_col_en = chose_col_en.Substring(0, chose_col_en.Length - 1);
                                    }
                                    if (chose_col_qi.Length > 1)
                                    {
                                        chose_col_qi = chose_col_qi.Substring(0, chose_col_qi.Length - 1);
                                    }
                                    if (chose_col_value.Length > 1)
                                    {
                                        chose_col_value = chose_col_value.Substring(0, chose_col_value.Length - 1);
                                    }

                                    if (tablekey.Length > 1)
                                    {
                                        tablekey = tablekey.Substring(0, tablekey.Length - 1);
                                    }
                                    var mapping_qi_col = chose_col_qi.Split(',');
                                    if (!string.IsNullOrEmpty(before_qi_col))
                                    {


                                        if (!string.IsNullOrEmpty(before_gen_setting))
                                        {
                                            var bf_qi_col = before_qi_col.Split(',');
                                            var gen_before_val = before_gen_setting.Split('*');
                                            var gen_lv1_valarr = gen_before_val[1].Split(',');
                                            var gen_lv2_valarr = gen_before_val[2].Split(',');
                                            var gen_final_lv1 = "";
                                            //var gen
                                            var gen_final_lv2 = "";
                                            for (int z = 0; z < mapping_qi_col.Length; z++)
                                            {
                                                var qi_col_val = mapping_qi_col[z].Split('-');
                                                var qi_select_val = "";
                                                for (int w = 0; w < bf_qi_col.Length; w++)
                                                {
                                                    var bf_qo_val = bf_qi_col[w].Split('-');
                                                    if (qi_col_val[0] == bf_qo_val[0])
                                                    {
                                                        qi_select_val = w.ToString();
                                                    }

                                                }
                                                if (qi_select_val == "")
                                                {
                                                    gen_final_lv1 += "0" + ",";
                                                    gen_final_lv2 += "0" + ",";
                                                }
                                                else
                                                {
                                                    gen_final_lv1 += gen_lv1_valarr[int.Parse(qi_select_val)] + ",";
                                                    gen_final_lv2 += gen_lv2_valarr[int.Parse(qi_select_val)] + ",";
                                                }
                                            }
                                            gen_final_lv1 = gen_final_lv1.Substring(0, gen_final_lv1.Length - 1);
                                            gen_final_lv2 = gen_final_lv2.Substring(0, gen_final_lv2.Length - 1);
                                            final_gen_setting_value = tbname + "*" + gen_final_lv1 + "*" + gen_final_lv2;
                                        }

                                    }
                                    //insert SampleTable
                                    log.Info("pid :" + pid);
                                    log.Info("pro_tb :" + tbname);
                                    log.Info("chose_col_en :" + chose_col_en);
                                    log.Info("chose_col_cht :" + chose_col_cht);
                                    log.Info("chose_col_qi :" + chose_col_qi);
                                    log.Info("tablekey :" + tablekey);
                                    log.Info("chose_col_value :" + chose_col_value);
                                    log.Info("final_gen_setting_value :" + final_gen_setting_value);
                                    log.Info("tbcols :" + tbcols);


                                    var updatestresult = proj_Service.UpdateProjectSampleTableSettingValue(pid, chose_col_en, chose_col_cht, chose_col_qi, tablekey, tbcols, final_gen_setting_value, tbname);
                                    if (updatestresult)
                                    {
                                        //更新到step3
                                        var prostatus = mydbhelper.UpdateProjectStauts(int.Parse(pid), 4, "概化規則設定");
                                        log.Info("update status 3 概化規則");
                                        if (prostatus)
                                        {
                                            isUpdate = true;
                                        }

                                    }
                                }
                            }
                        }

                    }
                    //return true;
                }
                else
                {
                    //return false;
                }
            }
            catch (Exception ex)
            {
                string errormsg = ex.Message.ToString();
                log.Error("UpdateColumnMsg Exception :" + errormsg);

            }
            return isUpdate;
        }

        //[HttpGet("UpdateColumnMsg")]
        //public bool UpdateColumnMsg(string pid, string pname, string selectvaluecol)
        //{
        //    bool isUpdate = false;
        //    log.Info("UpdateColumnMsg API");
        //    log.Info("UpdateColumnMsg API selectvaluecol :" + selectvaluecol);
        //    if (pid == "")
        //    {
        //        return false;
        //    }
        //    try
        //    {
        //        if (selectvaluecol != "")
        //        {
        //            //select 資料-比對寫入
        //            //< option value = "1" > 間接識別 </ option >
        //            //                                     < option value = "2" > 敏感資料 </ option >
        //            //                                      < option value = "3" > 直接識別 </ option >
        //            //                                       < option value = "4" selected = "selected" > 不處理 </ option >
        //            //                                          < option value = "0" > 不選用 </ option >
        //            //"4,4,3,0,4,4,4,4,4,1,1,4,0,2,0,0"
        //            var tbcolarray = selectvaluecol.Split('|');
        //            for (int x = 0; x < tbcolarray.Length; x++)
        //            {
        //                if (tbcolarray[x] != "")
        //                {
        //                    string tbselectvalue = tbcolarray[x];
        //                    var tbcollst = tbcolarray[x].Split('*');
        //                    string tbname = tbcollst[0];
        //                    string tbcols = tbcollst[1];
        //                    var colarray = tbcols.Split(',');
        //                    var lstSampleTB = proj_Service.SelectProjSampleTable(pid, tbname);
        //                    if (lstSampleTB.Count > 0)
        //                    {
        //                        string chose_col_cht = "";
        //                        string chose_col_en = "";
        //                        string chose_col_qi = "";
        //                        string chose_col_value = "";
        //                        // string chose_col_value = "";
        //                        string tablekey = "";
        //                        foreach (var item in lstSampleTB)
        //                        {
        //                            var col_cht = item.pro_col_cht;
        //                            var col_en = item.pro_col_en;
        //                            var col_cht_array = col_cht.Split(',');
        //                            var col_en_array = col_en.Split(',');
        //                            var bef_col = item.after_col_value;
        //                            var qi_value = item.qi_col;
        //                            var qi_settingvalue = item.gen_qi_settingvalue;
        //                            if (bef_col == "") //如果第一次 所以沒有before 等於這次
        //                                bef_col = tbcols;

        //                            if (bef_col != tbcols ) //資料庫內與這次更新不同
        //                            {

        //                                var bef_col_arr = bef_col.Split(',');
        //                                for (int i = 0; i < colarray.Length; i++)
        //                                {
        //                                    var col_val = "";
        //                                    for(int z=0;z <bef_col_arr.Length;z++)
        //                                    {
        //                                        if (colarray[i] == bef_col_arr[z])
        //                                        {
        //                                            col_val = colarray[i].ToString();
        //                                        }
        //                                        else //不同需比較QI
        //                                        {
        //                                            col_val = colarray[i].ToString();
        //                                            // if ==1 ==2  間接或敏感
        //                                            if(colarray[i]=="1")
        //                                            {
        //                                                if(bef_col_arr[z]!="1")
        //                                                {
        //                                                    if(bef_col_arr[z] == "2")
        //                                                    {

        //                                                    }
        //                                                }

        //                                            }
        //                                        }
        //                                    }

        //                                    switch (col_val)
        //                                    {
        //                                        case "0": //不選用
        //                                            break;
        //                                        case "1": //間接
        //                                            chose_col_cht += col_cht_array[i].ToString() + ",";
        //                                            chose_col_qi += col_cht_array[i].ToString() + "-1" + ",";
        //                                            chose_col_en += col_en_array[i].ToString() + ",";
        //                                            chose_col_value += colarray[i].ToString() + ",";
        //                                            break;
        //                                        case "2": //敏感
        //                                            chose_col_cht += col_cht_array[i].ToString() + ",";
        //                                            chose_col_qi += col_cht_array[i].ToString() + "-2" + ",";
        //                                            chose_col_en += col_en_array[i].ToString() + ",";
        //                                            chose_col_value += colarray[i].ToString() + ",";
        //                                            break;
        //                                        case "3": // 直接
        //                                            chose_col_cht += col_cht_array[i].ToString() + ",";
        //                                            tablekey += col_cht_array[i].ToString() + ",";
        //                                            chose_col_en += col_en_array[i].ToString() + ",";
        //                                            chose_col_value += colarray[i].ToString() + ",";
        //                                            break;
        //                                        case "4": //不處理
        //                                            chose_col_cht += col_cht_array[i].ToString() + ",";
        //                                            //chose_col_qi += col_cht_array[i].ToString() + ",";
        //                                            chose_col_en += col_en_array[i].ToString() + ",";
        //                                            chose_col_value += colarray[i].ToString() + ",";
        //                                            break;
        //                                    }
        //                                }
        //                            }
        //                            else
        //                            {
        //                                for (int i = 0; i < colarray.Length; i++)
        //                                {
        //                                    switch (colarray[i].ToString())
        //                                    {
        //                                        case "0": //不選用
        //                                            break;
        //                                        case "1": //間接
        //                                            chose_col_cht += col_cht_array[i].ToString() + ",";
        //                                            chose_col_qi += col_cht_array[i].ToString() + "-1" + ",";
        //                                            chose_col_en += col_en_array[i].ToString() + ",";
        //                                            chose_col_value += colarray[i].ToString() + ",";
        //                                            break;
        //                                        case "2": //敏感
        //                                            chose_col_cht += col_cht_array[i].ToString() + ",";
        //                                            chose_col_qi += col_cht_array[i].ToString() + "-2" + ",";
        //                                            chose_col_en += col_en_array[i].ToString() + ",";
        //                                            chose_col_value += colarray[i].ToString() + ",";
        //                                            break;
        //                                        case "3": // 直接
        //                                            chose_col_cht += col_cht_array[i].ToString() + ",";
        //                                            tablekey += col_cht_array[i].ToString() + ",";
        //                                            chose_col_en += col_en_array[i].ToString() + ",";
        //                                            chose_col_value += colarray[i].ToString() + ",";
        //                                            break;
        //                                        case "4": //不處理
        //                                            chose_col_cht += col_cht_array[i].ToString() + ",";
        //                                            //chose_col_qi += col_cht_array[i].ToString() + ",";
        //                                            chose_col_en += col_en_array[i].ToString() + ",";
        //                                            chose_col_value += colarray[i].ToString() + ",";
        //                                            break;
        //                                    }
        //                                }
        //                            }
        //                            if (chose_col_cht.Length > 1)
        //                            {
        //                                chose_col_cht = chose_col_cht.Substring(0, chose_col_cht.Length - 1);
        //                            }
        //                            if (chose_col_en.Length > 1)
        //                            {
        //                                chose_col_en = chose_col_en.Substring(0, chose_col_en.Length - 1);
        //                            }
        //                            if (chose_col_qi.Length > 1)
        //                            {
        //                                chose_col_qi = chose_col_qi.Substring(0, chose_col_qi.Length - 1);
        //                            }
        //                            if (chose_col_value.Length > 1)
        //                            {
        //                                chose_col_value = chose_col_value.Substring(0, chose_col_value.Length - 1);
        //                            }

        //                            if (tablekey.Length > 1)
        //                            {
        //                                tablekey = tablekey.Substring(0, tablekey.Length - 1);
        //                            }
        //                            //如果前面改了 QI欄位，後面也必須變動
        //                            //先比對
        //                            if(tbcols!=bef_col)
        //                            {

        //                            }
        //                            //insert SampleTable
        //                            log.Info("pid :" + pid);
        //                            log.Info("pro_tb :" + tbname);
        //                            log.Info("chose_col_en :" + chose_col_en);
        //                            log.Info("chose_col_cht :" + chose_col_cht);
        //                            log.Info("chose_col_qi :" + chose_col_qi);
        //                            log.Info("tablekey :" + tablekey);
        //                            log.Info("chose_col_value :" + chose_col_value);
        //                            log.Info("tbcols :" + tbcols);
        //                            var updatestresult = proj_Service.UpdateProjectSampleTable(pid, chose_col_en, chose_col_cht, chose_col_qi, tablekey, tbcols, "", tbname);
        //                            if (updatestresult)
        //                            {
        //                                //更新到step3
        //                                var prostatus = mydbhelper.UpdateProjectStauts(int.Parse(pid), 3, "概化規則設定");
        //                                log.Info("update status 3 概化規則");
        //                                if (prostatus)
        //                                {
        //                                    isUpdate = true;
        //                                }

        //                            }
        //                        }
        //                    }
        //                }

        //            }
        //            //return true;
        //        }
        //        else
        //        {
        //            //return false;
        //        }
        //    }
        //    catch (Exception ex)
        //    {
        //        string errormsg = ex.Message.ToString();
        //        log.Error("UpdateColumnMsg Exception :" + errormsg);

        //    }
        //    return isUpdate;
        //}

        private string GetQiSelectName(string selectvalue)
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
                    getQiSelectName = "數字位數";
                    break;
                case "5":
                    getQiSelectName = "數字區間(年齡)";
                    break;
                case "6":
                    getQiSelectName = "數字區間(金額)";
                    break;
                case "7":
                    getQiSelectName = "自訂";
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
                    getQiSelectName = "數字位數";
                    break;
                case "5":
                    getQiSelectName = "數字區間(年齡)";
                    break;
                case "6":
                    getQiSelectName = "數字區間(金額)";
                    break;
                case "7":
                    getQiSelectName = "自訂";
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
        [HttpGet("Generalizationasync")]
        public async Task<bool> GeneralizationasyncAsync(string pid, string pname, string selectqivalue, string k_value, string tablename)
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

                    var lstSampleTB = proj_Service.SelectProjSampleTable(pid, tbarray[i].ToString());
                    if (lstSampleTB == null)
                    {
                        return false;
                    }

                    tablelst = tbl + (i + 1).ToString();
                    if (lstSampleTB.Count > 0)
                    {
                        foreach (var item in lstSampleTB)
                        {
                            col_en = item.after_col_en;
                            col_cht = item.after_col_cht;
                            qi_value = item.qi_col;
                        }
                    }
                    genJson += genJsonRp.GetGenJsonAPI(pid, projStep, pname, col_en, col_cht, tablelst, tbarray[i].ToString(), qi_value, selectqivalue) + ",";
                    var col_gentb_arr = selectqivalue.Split('|');
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
                                var updatestresult = proj_Service.UpdateProjectSampleTableQI(pid, k_value, col_gentb_arr[b], tbarray[i]);
                            }
                        }
                    }
                }
                genJson = genJson.Substring(0, genJson.Length - 1);
                log.Info("gen Json Level 1 : " + genJson);
                StringBuilder sb = new StringBuilder();
                //sb.Append("{");
                sb.AppendLine("\"projID\":\"" + pid + "\",");
                sb.AppendLine("\"projStep\":\"" + projStep + "\",");
                sb.AppendLine("\"projName\":\"" + pname + "\",");
                sb.AppendLine("\"mainInfo\":{" + genJson.Substring(0, genJson.Length - 1));
                sb.AppendLine("}");
                //sb.AppendLine("}");
                var memberacc = "deidadmin";
                var memberId = "1";
                string genjsonstr = "{\"projID\":\"" + pid + "\", \"projStep\":\"" + projStep + "\",\"projName\":\"" + pname + "\",\"userAccount\":\"" + memberacc + "\",\"userId\":\"" + memberId + "\",\"mainInfo\": {" + genJson + "}}}";
                //genjsonstr = String.Format(genjsonstr, pid, projStep, pname, genJson);
                // byte[] byteServer = Encoding.GetEncoding("utf-8").GetBytes(sb.ToString());
                genjsonstr = genjsonstr.Replace('\\', ' ');
                log.Info("WebAPI Json Gen Format : " + genjsonstr);

                byte[] byteServer = Encoding.GetEncoding("utf-8").GetBytes(genjsonstr);

                //參數編成 Base64 字串
                string JsonServer = Convert.ToBase64String(byteServer);

                APIModel apiModel = new APIModel
                {
                    jsonBase64 = JsonServer
                };

                string strapi = JsonHelper.SerializeObject(apiModel);
                //var apirestult=HttpHelper.PostUrl("getServerFolder", "{\"jsonBase64\":\"eyJwcm9qTmFtZSI6ICJ0ZXN0X2ltcG9ydF9hbGwiLCAicHJvalN0ZXAiOiAiZ2V0U2VydmVyRm9sZGVyIiwgInByb2pJRCI6ICIxIn0=\"}");                
                var apirestult = HttpHelper.PostUrl("Generalization_async", strapi);
                //var apirestult = await httphelper.PostUrl_async("Generalization_async", strapi);
                if (apirestult != "")
                {
                    JObject apiresultJsobj = JObject.Parse(apirestult);
                    string apibase641 = apiresultJsobj["jsonBase64"].ToString();
                    var jsapiresults = Encoding.UTF8.GetString(Convert.FromBase64String(apibase641));
                    log.Info("gen return json format : " + jsapiresults);
                    JObject apidecode = JObject.Parse(jsapiresults);
                    string apistatus = apidecode["status"].ToString();
                    if (apistatus != "")
                    {
                        if (apistatus == "1")
                        {
                            List<ProjectSparkMan> ojString = new List<ProjectSparkMan>();
                            ProjectSparkMan psman = new ProjectSparkMan();
                            psman.celery_id = apidecode["celeryID"].ToString();
                            psman.app_id = apidecode["sparkAppID"].ToString();
                            psman.step = "Gen";
                            psman.stepstatus = 4;
                            //TODO
                            //增加欄位 step  用已確認步驟
                            psman.project_id = int.Parse(pid);
                            log.Info("celeryID : " + apidecode["celeryID"].ToString());
                            log.Info("sparkAppID : " + apidecode["sparkAppID"].ToString());
                            log.Info("step : " + "Gen");
                            log.Info("stepstatus : 4");
                            ojString.Add(psman);
                            var sparkstatus = mydbhelper.InsertSparkStauts(ojString);

                            //更新系統狀態
                            if (sparkstatus)
                            {
                                //update ProjectSampleTable
                                //var updatestresult = proj_Service.UpdateProjectSampleTableQI(pid, k_value, selectqivalue);
                                //if (updatestresult)
                                //{
                                //更新到step3
                                var prostatus = mydbhelper.UpdateProjectStauts(int.Parse(pid), 6, "概化規則設定中....");
                                if (prostatus)
                                {
                                    isGen = true;
                                }

                                //寫入spark status

                                //}
                                isGen = true;
                            }
                        }
                        else
                        {
                            isGen = false;
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

        public class ProjectStatusInputModel
        {
            public int k_project_id { get; set; }
            public string project_name { get; set; }
            public string file_name { get; set; }
            public string aes_col { get; set; }
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

        [HttpGet("k_report")]
        ///
        //public IActionResult k_checkstatus(string project_name)
        public IActionResult k_report([FromQuery] ProjectStatusInputModel inputModel)
        {
            log.Info("k_checkstatus 查詢狀態 WebAPI");
            string aes_col = inputModel.aes_col;
            log.Info("aes_col :" + aes_col);
            int project_id = inputModel.k_project_id;
            string jsonString = "";
            var responseList = new List<object>();
            var lstdatastructure = new List<DataStructure>();
            var warnning_cols = new List<Warnning_col>();

            try
            {
                var lst = proj_Service.SelectProjSampleTB(project_id.ToString());
                if (lst != null)
                {
                    if (lst.Count > 0)
                    {
                        string pro_tb = "";
                        string suprate = "";
                        int minKvalue = 0;
                        int tablecount = 0;
                        int k_tablecount = 0;
                        int k_supcount = 0;
                        foreach (var item in lst)
                        {
                            pro_tb = item.pro_tb;
                            suprate = item.supRate;
                            minKvalue = item.minKvalue;
                            tablecount = item.tableCount;
                            k_tablecount = item.tableDisCount;
                            k_supcount = item.supCount;

                            var qi_genstr = item.gen_qi_settingvalue;

                            var qi_col = item.qi_col;

                            var colqiarr = qi_col.Split(',');
                            var keylabel = item.tablekeycol;
                            var keyjson = "";


                            if (keylabel != "")
                            {
                                var keyarr = keylabel.Split(',');
                               
                                if (keyarr.Length > 0)
                                {
                                    for (int z = 0; z < keyarr.Length; z++)
                                    {
                                        //current_setting_report1_html += String.Format(qi_html, keyarr[z], keyarr[z], _localizer.Text.dir_id, "hash");
                                        var dataprocess = "Hash";
                                        if (aes_col != null)
                                        {
                                            if (aes_col.Length > 0)
                                            {
                                                var aesarr = aes_col.Split(',');
                                                if (aesarr.Length > 0)
                                                {
                                                    for (int i = 0; i < aesarr.Length; i++)
                                                    {
                                                        if (keyarr[z] == aesarr[i])
                                                        {
                                                            dataprocess = "AES";
                                                            break;
                                                        }
                                                    }
                                                }
                                            }
                                        }
                                        var jsonObject = new DataStructure
                                        {
                                            col_name = keyarr[z],
                                            col_setting = "直接識別",
                                            col_process = "hash"
                                        };

                                        lstdatastructure.Add(jsonObject);
                                    }
                                }
                            }

                            //qi
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

                                        var jsonObject = new DataStructure
                                        {
                                            col_name = name,
                                            col_setting = colcheck,
                                            col_process = g_data
                                        };

                                        lstdatastructure.Add(jsonObject);
                                    }
                                }
                            }

                            //warn
                            var warn_collist = item.warning_col;
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
                                        //warning_html_table += String.Format(warning_html, warn_colname_arr[i], warn_colval_arr[i]);
                                        var jsonObject = new Warnning_col
                                        {
                                            warnning_col = warn_colname_arr[i],
                                            warnning_count = int.Parse(warn_colval_arr[i])
                                        };

                                        warnning_cols.Add(jsonObject);
                                    }

                                }
                                else
                                {
                                    var jsonObject = new Warnning_col
                                    {
                                        warnning_col = "No Column",
                                        warnning_count = 0
                                    };

                                    warnning_cols.Add(jsonObject);
                                }
                                //warning_html_table += ",";

                            }
                        }

                        var datasetInfo = new DatasetInfo
                        {
                            ds_name = pro_tb,
                            ds_count = tablecount,
                            k_ds_count = k_tablecount,
                            k_sup_count = k_supcount,
                            ds_suprate = suprate,
                            risk_k = minKvalue.ToString()
                        };

                        var kreport = new k_report
                        {
                            datasetInfo = datasetInfo,
                            dataStructure = lstdatastructure,
                            warnning_col = warnning_cols
                        };

                        responseList.Add(kreport);
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
                log.Error("k_report Exception : " + errormsg);
                return BadRequest(new { status = -2, msg = errormsg });
            }
            return Json(responseList);
        }


        [HttpGet("k_checkstatus")]
        ///
        //public IActionResult k_checkstatus(string project_name)
        public IActionResult k_checkstatus([FromQuery] ProjectStatusInputModel inputModel)
        {
            log.Info("k_checkstatus 查詢狀態 WebAPI");
            string projectName = inputModel.project_name;
            int project_id = 0;
            log.Info("project_name :" + projectName);
            string jsonString = "";
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
                    if (lstproject != null)
                    {
                        if (lstproject.Count > 0)
                        {
                            foreach (var item in lstproject)
                            {
                                var proj_status = item.project_status;
                                string statusname = "";
                                project_id = item.Project_id;
                                string return_url = _configuration["K_WebAPI:URL"]; ;
                                switch (proj_status)
                                {
                                    case 0:
                                        statusname = "新建專案";
                                        return_url += "/ProjectStep/Step1?proj_id=" + WebUtility.UrlEncode(item.Project_id.ToString()) + "&project_name=" + WebUtility.UrlEncode(item.project_name) + "&stepstatus=" + WebUtility.UrlEncode(item.project_status.ToString()) + "&project_cht=" + WebUtility.UrlEncode(item.project_cht); ;
                                        break;
                                    case 1:
                                        statusname = "匯入資料";
                                        return_url += "/ProjectStep/Step1?proj_id=" + WebUtility.UrlEncode(item.Project_id.ToString()) + "&project_name=" + WebUtility.UrlEncode(item.project_name) + "&stepstatus=" + WebUtility.UrlEncode(item.project_status.ToString()) + "&project_cht=" + WebUtility.UrlEncode(item.project_cht); ;
                                        break;
                                    case 2:
                                        statusname = "資料匯入中";
                                        return_url = "";
                                        break;
                                    case 3:
                                        statusname = "欄位屬性設定";
                                        return_url += "/ProjectStep/Step2?proj_id=" + WebUtility.UrlEncode(item.Project_id.ToString()) + "&project_name=" + WebUtility.UrlEncode(item.project_name) + "&stepstatus=" + WebUtility.UrlEncode(item.project_status.ToString()) + "&project_cht=" + WebUtility.UrlEncode(item.project_cht); ;
                                        break;
                                    case 4:
                                        statusname = "概化處理";
                                        return_url += "/ProjectStep/Step3?proj_id=" + WebUtility.UrlEncode(item.Project_id.ToString()) + "&project_name=" + WebUtility.UrlEncode(item.project_name) + "&stepstatus=" + WebUtility.UrlEncode(item.project_status.ToString()) + "&project_cht=" + WebUtility.UrlEncode(item.project_cht); ;
                                        break;
                                    case 5:
                                        statusname = "概化預覽";
                                        return_url += "/ProjectStep/Step3?proj_id=" + WebUtility.UrlEncode(item.Project_id.ToString()) + "&project_name=" + WebUtility.UrlEncode(item.project_name) + "&stepstatus=" + WebUtility.UrlEncode(item.project_status.ToString()) + "&project_cht=" + WebUtility.UrlEncode(item.project_cht); ;
                                        break;
                                    case 6:
                                        statusname = "概化處理中";
                                        return_url = "";
                                        break;
                                    case 7:
                                        statusname = "資料K匿名";
                                        return_url = "";
                                        //return_url += "/ProjectStep/Step4?proj_id=" + WebUtility.UrlEncode(item.Project_id.ToString()) + "&project_name=" + WebUtility.UrlEncode(item.project_name) + "&stepstatus=" + WebUtility.UrlEncode(item.project_status.ToString()) + "&project_cht=" + WebUtility.UrlEncode(item.project_cht); ;
                                        break;
                                    case 8:
                                        statusname = "資料K匿名處理中";
                                        return_url = "";
                                        break;
                                    case 9:
                                        statusname = "查看報表";
                                        return_url += "/ProjectStep/Step6?proj_id=" + WebUtility.UrlEncode(item.Project_id.ToString()) + "&project_name=" + WebUtility.UrlEncode(item.project_name) + "&stepstatus=" + WebUtility.UrlEncode(item.project_status.ToString()) + "&project_cht=" + WebUtility.UrlEncode(item.project_cht); ;
                                        
                                        break;
                                    case 10:
                                        statusname = "資料匯出中";
                                        return_url = "";
                                        break;
                                    case 14:
                                        proj_status = 10;
                                        statusname = "資料匯出中";
                                        return_url = "";
                                        break;
                                    case 11:
                                        statusname = "資料下載";
                                        return_url += "/ProjectStep/Step6?proj_id=" + WebUtility.UrlEncode(item.Project_id.ToString()) + "&project_name=" + WebUtility.UrlEncode(item.project_name) + "&stepstatus=" + WebUtility.UrlEncode(item.project_status.ToString()) + "&project_cht=" + WebUtility.UrlEncode(item.project_cht); ;
                                        break;
                                    case 94:
                                        proj_status =95;
                                        statusname = "資料匯出錯誤";
                                        return_url += "/ProjectStep/Step6?proj_id=" + WebUtility.UrlEncode(item.Project_id.ToString()) + "&project_name=" + WebUtility.UrlEncode(item.project_name) + "&stepstatus=" + WebUtility.UrlEncode(item.project_status.ToString()) + "&project_cht=" + WebUtility.UrlEncode(item.project_cht); ;
                                        break;
                                    case 96:
                                        proj_status =94;
                                        statusname = "去識別化錯誤";
                                        return_url += "/ProjectStep/Step3?proj_id=" + WebUtility.UrlEncode(item.Project_id.ToString()) + "&project_name=" + WebUtility.UrlEncode(item.project_name) + "&stepstatus=" + WebUtility.UrlEncode(item.project_status.ToString()) + "&project_cht=" + WebUtility.UrlEncode(item.project_cht); ;
                                        break;
                                    case 97:
                                        proj_status =94;
                                        statusname = "去識別化錯誤";
                                        return_url += "/ProjectStep/Step3?proj_id=" + WebUtility.UrlEncode(item.Project_id.ToString()) + "&project_name=" + WebUtility.UrlEncode(item.project_name) + "&stepstatus=" + WebUtility.UrlEncode(item.project_status.ToString()) + "&project_cht=" + WebUtility.UrlEncode(item.project_cht); ;
                                        break;
                                    case 98:
                                        proj_status =93;
                                        statusname = "概化處理錯誤";
                                        return_url += "/ProjectStep/Step3?proj_id=" + WebUtility.UrlEncode(item.Project_id.ToString()) + "&project_name=" + WebUtility.UrlEncode(item.project_name) + "&stepstatus=" + WebUtility.UrlEncode(item.project_status.ToString()) + "&project_cht=" + WebUtility.UrlEncode(item.project_cht); ;
                                        break;
                                    case 92:
                                        statusname = "資料匯入錯誤";
                                        return_url += "/ProjectStep/Step1?proj_id=" + WebUtility.UrlEncode(item.Project_id.ToString()) + "&project_name=" + WebUtility.UrlEncode(item.project_name) + "&stepstatus=" + WebUtility.UrlEncode(item.project_status.ToString()) + "&project_cht=" + WebUtility.UrlEncode(item.project_cht); ;
                                        break;
                                    case 93:
                                        proj_status =94;
                                        statusname = "去識別化錯誤";
                                        return_url += "/ProjectStep/Step3?proj_id=" + WebUtility.UrlEncode(item.Project_id.ToString()) + "&project_name=" + WebUtility.UrlEncode(item.project_name) + "&stepstatus=" + WebUtility.UrlEncode(item.project_status.ToString()) + "&project_cht=" + WebUtility.UrlEncode(item.project_cht); ;
                                        break;
                                    default:
                                        statusname = "資料處理中";
                                        return_url = "";
                                        break;

                                }
                                var responseObject = new
                                {
                                    status = 1,
                                    msg = "",
                                    obj = new
                                    {
                                        project_id = project_id,
                                        project_status =proj_status,
                                        status_name = statusname,
                                        return_url = return_url
                                    }
                                };

                                // 将匿名对象转换为 JSON 字符串
                                jsonString = JsonConvert.SerializeObject(responseObject);
                                log.Info("check K status :" + jsonString);
                                responseList.Add(responseObject);
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
                log.Error("k_checkstatus Exception : " + errormsg);
                return BadRequest(new { status = -1, msg = errormsg });
            }
            return Json(responseList);
        }


        [HttpGet("k_reset")]
        ///
        //public IActionResult k_checkstatus(string project_name)
        public IActionResult k_reset([FromQuery] ProjectStatusInputModel inputModel)
        {
            log.Info("k_reset 重設專案 WebAPI");
            //string projectName = inputModel.project_name;
            int project_id = inputModel.k_project_id;
            log.Info("project_id :" + project_id.ToString());
            log.Info("取消專案 ");
            var responseList = new List<object>();
            //log.Info("取消專案 ID:" + project_id.ToString());
            //log.Info("取消專案 名稱:" + pname);
            try
            {
                mydbhelper.UpdateProjectStatus(project_id, 3);
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
                log.Error("k_checkstatus Exception : " + errormsg);
                return BadRequest(new { status = -1, msg = errormsg });
            }
            return Json(responseList);
        }

        [HttpGet("k_conn")]
        ///
        //public IActionResult k_checkstatus(string project_name)
        public IActionResult k_conn([FromQuery] ProjectStatusInputModel inputModel)
        {
            log.Info("k_conn 串接子系統");
            string projectName = inputModel.project_name;
            string filename = inputModel.file_name;
            var responseList = new List<object>();
            string project_id = "";
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
                  
                    string insertsql = "insert into T_Project(project_name,project_desc,project_path,export_path,projectowner_id,createtime,project_cht)values('" + projectName + "','" + projectName + "','" + projectName + "','" + projectName + "'," + "(select Id from T_Member where useraccount='deidadmin')" + ",Now(),'" + projectName + "');";
                    var result = mydbhelper.InsertDB(insertsql);
                    if (result)
                    {
                        var proId = mydbhelper.SelectProject(sql);
                        foreach (var item in proId)
                        {
                            project_id = item.Project_id.ToString();
                            log.Info("WebAPI InsertProject Insert ProjectStatus ");
                            
                            //var prostatussql = "insert into T_ProjectStatus(project_id,project_status,statusname,createtime)values(" + item.Project_id + ",0,'資料匯入處理中',now())";
                            var psresult = projService.InsertProjectStauts(item.Project_id, 0, "資料專案開啟");

                            //insert專案成功 匯入資料 
                            GetServerFolderJsonModel serverfolder = new GetServerFolderJsonModel
                            {
                                projName = projectName,
                                //serverfolder.projName = "test_import_all";
                                projStep = "import",
                                projID = item.Project_id.ToString(),
                                userAccount = "deidadmin",
                                userId = "1"
                            };
                            string serverfolderstr = JsonHelper.SerializeObject(serverfolder);
                            log.Info("Import Json String :" + serverfolderstr);
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
                            var apirestult = HttpHelper.PostUrl("ImportFile_PETs", strapi);
                            //var apirestult = await httphelper.PostUrl_async("ImportFile", strapi);

                            log.Info("Import File Json  Return String " + apirestult);
                            if (apirestult != "")
                            {
                                JObject apiresultJsobj = JObject.Parse(apirestult);
                                string apibase641 = apiresultJsobj["jsonBase64"].ToString();
                                var jsapiresults = Encoding.UTF8.GetString(Convert.FromBase64String(apibase641));
                                log.Info("ImportFile return JsonString :" + jsapiresults);
                             
                                JObject apidecode = JObject.Parse(jsapiresults);
                                string apistatus = apidecode["status"].ToString();
                                if (apistatus == "1")
                                {
                                    
                                    //更新系統狀態
                                    var prostatus = mydbhelper.UpdateProjectStauts(item.Project_id, 2, "資料匯入中");
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
                                else
                                {
                                    //delete project
                                    mydbhelper.DeleteProject(int.Parse(project_id));
                                    log.Info("刪除專案 成功");
                                    var mutiproj = new
                                    {
                                        status = -2,
                                        msg = "System Error",
                                        obj = new
                                        {

                                        }
                                    };

                                    //var jsonString = JsonConvert.SerializeObject(mutiproj);
                                    responseList.Add(mutiproj);
                                }

                            }
                            else
                            {
                                mydbhelper.DeleteProject(int.Parse(project_id));
                                log.Info("刪除專案 成功");

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
                log.Error("k_conn Exception : " + errormsg);
                mydbhelper.DeleteProject(int.Parse(project_id));
                log.Info("刪除專案 成功");

                return BadRequest(new { status = -1, msg = errormsg });
            }
            return Json(responseList);
        }



        [HttpGet("Generalization_InterAgent_Async")]
        ///
        public bool Generalization_InterAgent_Async(string pid, string pname, string selectqivalue, string k_value, string tablename)
        {

            bool isGen = false;
            //bool isUpdate = false;
            log.Info("Generalization_InterAgent_async 概化 WebAPI");
            log.Info("pid :" + pid);
            log.Info("pname :" + pname);
            log.Info("selectqivalue :" + selectqivalue);
            log.Info("k_value :" + k_value);
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

                    var lstSampleTB = proj_Service.SelectProjSampleTable(pid, tbarray[i].ToString());
                    if (lstSampleTB == null)
                    {
                        return false;
                    }

                    tablelst = tbl + (i + 1).ToString();
                    if (lstSampleTB.Count > 0)
                    {
                        foreach (var item in lstSampleTB)
                        {
                            col_en = item.after_col_en;
                            col_cht = item.after_col_cht;
                            qi_value = item.qi_col;
                        }
                    }
                    genJson += genJsonRp.GetGenJsonAPI(pid, projStep, pname, col_en, col_cht, tablelst, tbarray[i].ToString(), qi_value, selectqivalue) + ",";
                    var col_gentb_arr = selectqivalue.Split('|');
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
                                //var updatestresult = proj_Service.UpdateProjectSampleTableQI(pid, k_value, col_gentb_arr[b], tbarray[i],"0","0","0");
                                var updatestresult = proj_Service.UpdateProjectSampleTableQI(pid, k_value, col_gentb_arr[b], tbarray[i]);
                            }
                        }
                    }
                }
                genJson = genJson.Substring(0, genJson.Length - 1);
                log.Info("gen Json Level 1 : " + genJson);
                StringBuilder sb = new StringBuilder();
                //sb.Append("{");
                sb.AppendLine("\"projID\":\"" + pid + "\",");
                sb.AppendLine("\"projStep\":\"" + projStep + "\",");
                sb.AppendLine("\"projName\":\"" + pname + "\",");
                sb.AppendLine("\"mainInfo\":{" + genJson.Substring(0, genJson.Length - 1));
                sb.AppendLine("}");
                //sb.AppendLine("}");
                string genjsonstr = "{\"projID\":\"" + pid + "\", \"projStep\":\"" + projStep + "\",\"projName\":\"" + pname + "\",\"mainInfo\": {" + genJson + "}}}";
                //genjsonstr = String.Format(genjsonstr, pid, projStep, pname, genJson);
                // byte[] byteServer = Encoding.GetEncoding("utf-8").GetBytes(sb.ToString());
                genjsonstr = genjsonstr.Replace('\\', ' ');
                log.Info("WebAPI Json Generalization_InterAgent_async Format : " + genjsonstr);

                byte[] byteServer = Encoding.GetEncoding("utf-8").GetBytes(genjsonstr);

                //參數編成 Base64 字串
                string JsonServer = Convert.ToBase64String(byteServer);

                APIModel apiModel = new APIModel
                {
                    jsonBase64 = JsonServer
                };

                string strapi = JsonHelper.SerializeObject(apiModel);
                //var apirestult=HttpHelper.PostUrl("getServerFolder", "{\"jsonBase64\":\"eyJwcm9qTmFtZSI6ICJ0ZXN0X2ltcG9ydF9hbGwiLCAicHJvalN0ZXAiOiAiZ2V0U2VydmVyRm9sZGVyIiwgInByb2pJRCI6ICIxIn0=\"}");                
                var apirestult = HttpHelper.PostUrl("Generalization_InterAgent_async", strapi);
                if (apirestult != "")
                {
                    JObject apiresultJsobj = JObject.Parse(apirestult);
                    string apibase641 = apiresultJsobj["jsonBase64"].ToString();
                    var jsapiresults = Encoding.UTF8.GetString(Convert.FromBase64String(apibase641));
                    log.Info("gen return json format : " + jsapiresults);
                    JObject apidecode = JObject.Parse(jsapiresults);
                    string apistatus = apidecode["status"].ToString();
                    if (apistatus != "")
                    {
                        if (apistatus == "1")
                        {
                            List<ProjectSparkMan> ojString = new List<ProjectSparkMan>();
                            ProjectSparkMan psman = new ProjectSparkMan();
                            psman.celery_id = apidecode["celeryID"].ToString();
                            psman.app_id = apidecode["sparkAppID"].ToString();
                            psman.step = "Gen";
                            psman.stepstatus = 4;
                            //TODO
                            //增加欄位 step  用已確認步驟
                            psman.project_id = int.Parse(pid);
                            log.Info("celeryID : " + apidecode["celeryID"].ToString());
                            log.Info("sparkAppID : " + apidecode["sparkAppID"].ToString());
                            log.Info("step : " + "Gen");
                            log.Info("stepstatus : 4");
                            ojString.Add(psman);
                            var sparkstatus = mydbhelper.InsertSparkStauts(ojString);

                            //更新系統狀態
                            if (sparkstatus)
                            {
                                //update ProjectSampleTable
                                //var updatestresult = proj_Service.UpdateProjectSampleTableQI(pid, k_value, selectqivalue);
                                //if (updatestresult)
                                //{
                                //更新到step3
                                var prostatus = mydbhelper.UpdateProjectStauts(int.Parse(pid), 6, "概化規則設定中....");
                                if (prostatus)
                                {
                                    isGen = true;
                                }

                                //寫入spark status

                                //}
                                isGen = true;
                            }
                        }
                        else
                        {
                            isGen = false;
                        }
                    }
                }

            }
            catch (Exception ex)
            {
                string errormsg = ex.Message;
                log.Error("Web API Generalization_InterAgent_async Exception : " + errormsg);

            }
            return isGen;
        }

        [HttpGet("GetqicolData")]
        public string GetqicolData(string pid, string pname)
        {
            log.Info("WebAPI GetqicolData ");
            log.Info("pid " + pid);
            log.Info("pname " + pname);
            string chose_col_qi = "";
            string keycol = "";
            //string returncol = "";
            string after_col_cht = "";
            string after_col_en = "";
            string pro_col_en = "";
            string pro_tb = "";
            string col_value = "";
            string returnstr = "";
            //select id 用 en
            //bool isUpdate = false;
            if (pid == "")
            {
                return "";
            }
            try
            {

                var lstSampleTB = proj_Service.SelectProjSampleTB(pid);
                if (lstSampleTB.Count > 0)
                {

                    foreach (var item in lstSampleTB)
                    {
                        pro_tb = item.pro_tb;
                        chose_col_qi = item.qi_col;
                        keycol = item.tablekeycol;
                        after_col_cht = item.after_col_cht;
                        after_col_en = item.after_col_en;
                        pro_col_en = item.pro_col_en;
                        col_value = item.after_col_value;
                        returnstr = pro_tb + "*" + pro_col_en + "*" + col_value + "|";
                    }
                }

                returnstr = returnstr.Substring(0, returnstr.Length - 1);
                //return true;
                return returnstr;
            }
            catch (Exception ex)
            {
                string errormsg = ex.Message;
                log.Error("GetqicolData Exception :" + errormsg);
                return "";
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

        [HttpGet("GetProjectOwner")]
        public string GetProjectOwner()
        {
            var list = mydbhelper.SelectMember("select * from T_Member;");
            string selecthtml = "<select class=\"form - control\" id=\"p_owner\" name=\"\">< option value = \"\" > 請選擇 </ option >< option value = \"\" ></ option ></ select > ";
            string optionvalue = "";
            foreach (var item in list)
            {
                optionvalue += string.Format("< option value = \"{0}\" >{1}</ option >", item.Id, item.UserAccount);
            }
            selecthtml = string.Format(selecthtml, optionvalue);

            return selecthtml;
        }


        /// <summary>
        /// 匯入資料
        /// </summary>
        /// <param name="p_dsname">Adult_test</param>
        /// <param name="pid">1</param>
        /// <returns></returns>
        [HttpGet("ImportData")]
        public string ImportData(string p_dsname, string pid)
        //public async Task<string> ImportData(string p_dsname, string pid)
        {
            string returnmsg = "";
            log.Info("Web API ImportData");
            log.Info("pid " + pid);
            log.Info("pname " + p_dsname);
            try
            {
                //"{\"projName\": \"test_import_all\", \"projStep\": \"import\", \"projID\": \"1\"}"
                GetServerFolderJsonModel serverfolder = new GetServerFolderJsonModel
                {
                    projName = p_dsname,
                    //serverfolder.projName = "test_import_all";
                    projStep = "import",
                    projID = pid,
                    userAccount = "deidadmin",
                    userId = "1"
                };
                string serverfolderstr = JsonHelper.SerializeObject(serverfolder);
                log.Info("Import Json String :" + serverfolderstr);
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
                var apirestult = HttpHelper.PostUrl("ImportFile", strapi);
                //var apirestult = await httphelper.PostUrl_async("ImportFile", strapi);

                log.Info("Import File Json  Return String " + apirestult);
                if (apirestult != "")
                {
                    JObject apiresultJsobj = JObject.Parse(apirestult);
                    string apibase641 = apiresultJsobj["jsonBase64"].ToString();
                    var jsapiresults = Encoding.UTF8.GetString(Convert.FromBase64String(apibase641));
                    log.Info("ImportFile return JsonString :" + jsapiresults);
                    JObject apidecode = JObject.Parse(jsapiresults);
                    string apistatus = apidecode["status"].ToString();
                    if (apistatus == "1")
                    {
                        List<ProjectSparkMan> ojString = new List<ProjectSparkMan>();
                        ProjectSparkMan psman = new ProjectSparkMan();
                        psman.celery_id = apidecode["celeryID"].ToString();
                        psman.app_id = apidecode["sparkAppID"].ToString();
                        psman.step = "ImportFile";
                        psman.stepstatus = 0;
                        //TODO
                        //增加欄位 step  用已確認步驟
                        psman.project_id = int.Parse(pid);
                        log.Info("celeryID : " + apidecode["celeryID"].ToString());
                        log.Info("sparkAppID : " + apidecode["sparkAppID"].ToString());
                        log.Info("step : " + "ImportFile");
                        log.Info("stepstatus :0");
                        ojString.Add(psman);
                        var sparkstatus = mydbhelper.InsertSparkStauts(ojString);

                        //更新系統狀態
                        if (sparkstatus)
                        {
                            var prostatus = mydbhelper.UpdateProjectStauts(int.Parse(pid), 2, "資料匯入中");
                            if (prostatus)
                                returnmsg = "1";
                        }
                        else
                        {
                            string errMsg = "-1";
                            returnmsg = errMsg;
                        }
                    }
                    else
                    {
                        string errMsg = apidecode["errMsg"].ToString();
                        log.Error("ImportFile Return Json Error :" + errMsg);
                        returnmsg = "-2";
                    }

                    //"{\"status\": \"1\", \"celeryID\": \"14ed2515-6fa3-46b1-bb7a-3023dc26146c\", \"tblNames\": \"adult_id;adult_id_adult_testNA2;adult_id_post2w;
                    //adult;adult_id_pre2w\", \"projStep\": \"import\", \"time_async\": \"15.817054987\", \"sparkAppID\": \"application_1547630236814_0197\", \"dbName\": \"test_import_all\", \"errMsg\": \"\"}"

                }
                else
                {
                    log.Error("ImportFile Return Json Error : Session Timeout");
                    returnmsg = "-3";
                }
                return returnmsg;
            }
            catch (Exception ex)
            {
                log.Error("ImportFile Exception :" + ex.Message);
                return "-2";
            }
        }

        [HttpGet("SingleTableJob")]
        public string SingleTableJob(string pid, string pname, string tablename, string jobname)
        {
            string returnmsg = "";
            log.Info("Web API ExportData");
            log.Info("pid " + pid);
            log.Info("pname " + pname);
            string projStep = "export";
            try
            {
                //jsonDic_ = {
                //    'projID': '1',
                //    'projStep': 'export',
                //    'projName': 'test_project',
                //    'mainInfo': {
                //        'tbl_1': {
                //            'tblName': 'adult_id_post2w',
                //                           'location': 'local'
                //                           }
                //    }
                //}
                var lstSampleTB = proj_Service.SelectProjSampleTablebyId(pid);
                if (lstSampleTB == null)
                {
                    return "No Data";
                }
                int x = 1;
                string strmainInfo = "";
                string mainInfo = "{\"{0}\":{\"tblName\":\"{1}\",\"location\":\"local\"}}";
                foreach (var item in lstSampleTB)
                {
                    string tb = "tbl_" + x.ToString();
                    mainInfo = "{\"" + tb + "\":{\"tblName\":\"" + item.finaltblName + "\",\"location\":\"local\"}}";
                    strmainInfo += mainInfo + ",";
                    x++;
                }
                strmainInfo = strmainInfo.Substring(0, strmainInfo.Length - 1);
                string genjsonstr = "{\"projID\":\"" + pid + "\", \"projStep\":\"" + projStep + "\",\"projName\":\"" + pname + "\",\"mainInfo\": " + strmainInfo + "}";

                //"{\"projName\": \"test_import_all\", \"projStep\": \"import\", \"projID\": \"1\"}"
                genjsonstr = genjsonstr.Replace('\\', ' ');
                log.Info("WebAPI Json Gen Format : " + genjsonstr);

                byte[] byteServer = Encoding.GetEncoding("utf-8").GetBytes(genjsonstr);

                //參數編成 Base64 字串
                string JsonServer = Convert.ToBase64String(byteServer);

                APIModel apiModel = new APIModel
                {
                    jsonBase64 = JsonServer
                };

                string strapi = JsonHelper.SerializeObject(apiModel);
                //var apirestult=HttpHelper.PostUrl("getServerFolder", "{\"jsonBase64\":\"eyJwcm9qTmFtZSI6ICJ0ZXN0X2ltcG9ydF9hbGwiLCAicHJvalN0ZXAiOiAiZ2V0U2VydmVyRm9sZGVyIiwgInByb2pJRCI6ICIxIn0=\"}");                
                var apirestult = HttpHelper.PostUrl("ExportFile", strapi);
                if (apirestult != "")
                {
                    JObject apiresultJsobj = JObject.Parse(apirestult);
                    string apibase641 = apiresultJsobj["jsonBase64"].ToString();
                    var jsapiresults = Encoding.UTF8.GetString(Convert.FromBase64String(apibase641));
                    log.Info("gen return json format : " + jsapiresults);
                    JObject apidecode = JObject.Parse(jsapiresults);
                    string apistatus = apidecode["status"].ToString();
                    if (apistatus != "")
                    {
                        if (apistatus == "1")
                        {
                            List<ProjectSparkMan> ojString = new List<ProjectSparkMan>();
                            ProjectSparkMan psman = new ProjectSparkMan();
                            psman.celery_id = apidecode["celeryID"].ToString();
                            psman.app_id = apidecode["sparkAppID"].ToString();
                            psman.step = "exportfile";
                            psman.stepstatus = 5;
                            //TODO
                            //增加欄位 step  用已確認步驟
                            psman.project_id = int.Parse(pid);
                            log.Info("celeryID : " + apidecode["celeryID"].ToString());
                            log.Info("sparkAppID : " + apidecode["sparkAppID"].ToString());
                            log.Info("step : " + "export");
                            log.Info("stepstatus : 5");
                            ojString.Add(psman);
                            var sparkstatus = mydbhelper.InsertSparkStauts(ojString);

                            //更新系統狀態
                            if (sparkstatus)
                            {
                                //update ProjectSampleTable
                                //var updatestresult = proj_Service.UpdateProjectSampleTableQI(pid, k_value, selectqivalue);
                                //if (updatestresult)
                                //{
                                //更新到step3
                                var prostatus = mydbhelper.UpdateProjectStauts(int.Parse(pid), 8, "去識別化作業完成....");
                                if (prostatus)
                                {
                                    //isGen = true;
                                }

                                //寫入spark status

                                //}
                                // isGen = true;
                            }
                        }
                        else
                        {
                            //isGen = false;
                        }
                    }
                }
                return returnmsg;
            }
            catch (Exception ex)
            {
                log.Error("Export File Exception :" + ex.Message);
                return "-2";
            }
        }

        /// <summary>
        /// 
        /// </summary>
        /// <param name="pid"></param>
        /// <param name="p_dsname"></param>
        /// <returns></returns>
        [HttpGet("ExportData")]
        public bool ExportData(string pid, string p_dsname)
        {
            // string returnmsg = "";
            log.Info("Web API ExportData");
            log.Info("pid " + pid);
            log.Info("p_dsname " + p_dsname);
            string projStep = "export";
            try
            {
                //jsonDic_ = {
                //    'projID': '1',
                //    'projStep': 'export',
                //    'projName': 'test_project',
                //    'mainInfo': {
                //        'tbl_1': {
                //            'tblName': 'adult_id_post2w',
                //                           'location': 'local'
                //                           }
                //    }
                //}
                var lstSampleTB = proj_Service.SelectProjSampleTablebyId(pid);
                if (lstSampleTB == null)
                {
                    return false;
                }
                int x = 1;
                string strmainInfo = "";
                string mainInfo = "{\"{0}\":{\"tblName\":\"{1}\",\"location\":\"local\"}}";
                foreach (var item in lstSampleTB)
                {
                    string tb = "tbl_" + x.ToString();
                    mainInfo = "{\"" + tb + "\":{\"pro_tb\":\"" + item.pro_tb + "\",\"finaltblName\":\"" + item.finaltblName + "\",\"location\":\"local\"}}";
                    strmainInfo += mainInfo + ",";
                    x++;
                }
                strmainInfo = strmainInfo.Substring(0, strmainInfo.Length - 1);
                //string genjsonstr = "{\"projID\":\"" + pid + "\", \"projStep\":\"" + projStep + "\",\"projName\":\"" + p_dsname + "\",\"mainInfo\": " + strmainInfo + "}";
                string genjsonstr = "{\"projID\":\"" + pid + "\", \"projStep\":\"" + projStep + "\",\"projName\":\"" + p_dsname + "\",\"userAccount\":\"" + "deidadmin" + "\",\"userId\":\"" + "1" + "\",\"mainInfo\": " + strmainInfo + "}";

                //"{\"projName\": \"test_import_all\", \"projStep\": \"import\", \"projID\": \"1\"}"
                genjsonstr = genjsonstr.Replace('\\', ' ');
                log.Info("WebAPI Json Gen Format : " + genjsonstr);

                byte[] byteServer = Encoding.GetEncoding("utf-8").GetBytes(genjsonstr);

                //參數編成 Base64 字串
                string JsonServer = Convert.ToBase64String(byteServer);

                APIModel apiModel = new APIModel
                {
                    jsonBase64 = JsonServer
                };

                string strapi = JsonHelper.SerializeObject(apiModel);
                //var apirestult=HttpHelper.PostUrl("getServerFolder", "{\"jsonBase64\":\"eyJwcm9qTmFtZSI6ICJ0ZXN0X2ltcG9ydF9hbGwiLCAicHJvalN0ZXAiOiAiZ2V0U2VydmVyRm9sZGVyIiwgInByb2pJRCI6ICIxIn0=\"}");                
                log.Info("WebAPI Json Gen Json Base64 : " + strapi);
                //var apirestult = HttpHelper.PostUrl("ExportFile", strapi);
                var apirestult = HttpHelper.PostUrl("ExportFile_PETs", strapi);
                if (apirestult != "")
                {
                    JObject apiresultJsobj = JObject.Parse(apirestult);
                    string apibase641 = apiresultJsobj["jsonBase64"].ToString();
                    log.Info("WebAPI Json return Json Base64 : " + apibase641);
                    var jsapiresults = Encoding.UTF8.GetString(Convert.FromBase64String(apibase641));
                    log.Info("gen return json format : " + jsapiresults);
                    JObject apidecode = JObject.Parse(jsapiresults);
                    string apistatus = apidecode["status"].ToString();
                    if (apistatus != "")
                    {
                        if (apistatus == "1")
                        {
                            List<ProjectSparkMan> ojString = new List<ProjectSparkMan>();
                            ProjectSparkMan psman = new ProjectSparkMan();
                            psman.celery_id = apidecode["celeryID"].ToString();
                            psman.app_id = apidecode["sparkAppID"].ToString();
                            psman.step = "exportfile";
                            psman.stepstatus = 5;
                            //TODO
                            //增加欄位 step  用已確認步驟
                            psman.project_id = int.Parse(pid);
                            log.Info("celeryID : " + apidecode["celeryID"].ToString());
                            log.Info("sparkAppID : " + apidecode["sparkAppID"].ToString());
                            log.Info("step : " + "export");
                            log.Info("stepstatus : 5");
                            ojString.Add(psman);
                            var sparkstatus = mydbhelper.InsertSparkStauts(ojString);

                            //更新系統狀態
                            if (sparkstatus)
                            {
                                //update ProjectSampleTable
                                //var updatestresult = proj_Service.UpdateProjectSampleTableQI(pid, k_value, selectqivalue);
                                //if (updatestresult)
                                //{
                                //更新到step3
                                var prostatus = mydbhelper.UpdateProjectStauts(int.Parse(pid), 14, "匯出資料中....");
                                if (prostatus)
                                {
                                    //isGen = true;
                                }

                                //寫入spark status

                                //}
                                // isGen = true;
                            }
                        }
                        else
                        {
                            //isGen = false;
                        }
                    }
                }
                return true;
            }
            catch (Exception ex)
            {
                log.Error("Export File Exception :" + ex.Message);
                return false;
            }
        }

        [HttpGet("GetNotificationData")]
        public string GetNotificationData()
        {
            string returnmsg = "";
            //ProjectSparkMan
            int sparkjobcount = 0;
            string pname_cht = "";
            string step = "";
            string not_ntml = "";
            var jobstatusresult = mydbhelper.SelectProjectJobStatus();
            //log.Info("GetNotificationData");
            if (jobstatusresult == null)
            {
                var aaa = 0;
                // log.Info("Notification :" + "0筆");
            }
            else
            {
                //log.Info("共幾筆 Notification :" + jobstatusresult.Count);
            }

            if (jobstatusresult != null && jobstatusresult.Count > 0)
            {
                sparkjobcount = jobstatusresult.Count;
                foreach (var item in jobstatusresult)
                {
                    try
                    {
                        //log.Info("project_name :" + item.project_name);
                        //log.Info("job appid :" + item.app_id);
                        //log.Info("job step :" + item.step);
                        //log.Info("job stepstatus :" + item.stepstatus);
                        if (item.stepstatus == 100)
                        {
                            returnmsg = "100"; //完成
                        }
                        else
                        {
                            string appid = "";
                            appid = item.app_id;
                            returnmsg = item.stepstatus.ToString();
                            APISparkJobModel sparkmodel = new APISparkJobModel
                            {
                                applicationID = item.app_id
                            };
                            string strsparkstatus = JsonHelper.SerializeObject(sparkmodel);
                            //    log.Info("job json  :" + strsparkstatus);

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
                            if (apirestult != "")
                            {
                                JObject apiresultJsobj = JObject.Parse(apirestult);
                                string apibase641 = apiresultJsobj["jsonBase64"].ToString();
                                var jsapiresults = Encoding.UTF8.GetString(Convert.FromBase64String(apibase641));
                                //log.Info("web api return json :" + jsapiresults);
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
                                            if (item.step == "ImportFile")
                                            {
                                                var prostatus = mydbhelper.UpdateProjectStauts(item.project_id, 3, "資料集屬性判定");
                                                if (prostatus)
                                                {
                                                    //ViewData["ProjectStep"] = "2";
                                                }
                                            }
                                            else if (item.step == "Gen")
                                            {
                                                var prostatus = mydbhelper.UpdateProjectStauts(item.project_id, 7, "去識別化與風險設定處理");
                                                if (prostatus)
                                                {
                                                    //ViewData["ProjectStep"] = "2";
                                                }
                                            }
                                            else if (item.step == "kchecking_async")
                                            {
                                                var prostatus = mydbhelper.UpdateProjectStauts(item.project_id, 7, "去識別化與風險設定處理");
                                                if (prostatus)
                                                {

                                                    //delete ProjecteJobStatus
                                                }
                                            }
                                            else if (item.step == "risk")
                                            {
                                                var prostatus = mydbhelper.UpdateProjectStauts(item.project_id, 10, "可用性感興趣欄位選定");
                                                if (prostatus)
                                                {

                                                    //delete ProjecteJobStatus
                                                }
                                            }
                                            else if (item.step == "MLutility")
                                            {
                                                var prostatus = mydbhelper.UpdateProjectStauts(item.project_id, 12, "報表查看");
                                                if (prostatus)
                                                {

                                                    //delete ProjecteJobStatus
                                                }
                                            }
                                            else if (item.step == "exportfile")
                                            {
                                                var prostatus = mydbhelper.UpdateProjectStauts(item.project_id, 15, "去識別化完成");
                                                if (prostatus)
                                                {

                                                    //delete ProjecteJobStatus
                                                }
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
                    }
                    catch (Exception ex)
                    {
                        string errormsg = ex.Message.ToString();
                        log.Error("GetNotification Error :" + errormsg);
                    }

                    pname_cht = item.project_cht;
                    step = item.step;
                    not_ntml += "<li class=\"notification_dropdown_item\">" + "<img src=\"/images/noti_light.png\">" +
                                "<div class=\"text\"><p>" + item.project_cht + "  " + item.step + "</p><div class=\"time\">" + item.createtime.ToString("MM-dd") + "</div></div></li>";
                }
            }

            //add appStatus
            var lstappStatus = mydbhelper.SelectProjectAppStatus();
            if (lstappStatus.Count > 0)
            {
                sparkjobcount = sparkjobcount + lstappStatus.Count;
                foreach (var items in lstappStatus)
                {
                    not_ntml += "<li class=\"notification_dropdown_item\">" + "<img src=\"/images/noti_light.png\">" +
                                "<div class=\"text\"><p>" + pname_cht + "  " + items.Application_Name + "</p><div class=\"time\">" + items.Createtime.ToString("MM-dd") + "</div></div></li>";
                }
            }
            if (jobstatusresult != null)
            {
                string final_html = "<li class=\"notification_dropdown_item\">" + _localizer.Text.notification + "</li>" + not_ntml;
                returnmsg = sparkjobcount + "*" + final_html;
            }
            //組成 json 

            return returnmsg;
        }


        [HttpGet("GetStatusAppNotificationData")]
        public string GetStatusAppNotificationData()
        {
            string returnmsg = "";
            //ProjectSparkMan
            int sparkjobcount = 0;
            string pname_cht = "";
            string step = "";
            int jobcount_num = 50;
            string not_ntml = "";
            var jobcount = mydbhelper.SelectProjAppStatus();
            //log.Info("GetStatusAppNotificationData");
            //if (jobcount == null)
            //   // log.Info("GetStatusAppNotificationData 無資料 :" + "0筆");
            //else
            //    //log.Info("共幾筆 新的Notification :" + jobcount.Count);

            var jobstatusresult = mydbhelper.SelectProjAppStatusIsRead();
            //if (jobstatusresult == null)
            //    log.Info("Notification :" + "0筆");
            //else
            //    log.Info("共全部已讀資料幾筆 Notification :" + jobstatusresult.Count);

            #region sparkjob_management
            //if (jobstatusresult != null && jobstatusresult.Count > 0)
            //{
            //    sparkjobcount = jobstatusresult.Count;
            //    foreach (var item in jobstatusresult)
            //    {
            //        try
            //        {
            //            log.Info("project_name :" + item.);
            //            log.Info("job appid :" + item.app_id);
            //            log.Info("job step :" + item.step);
            //            log.Info("job stepstatus :" + item.stepstatus);
            //            if (item.stepstatus == 100)
            //            {
            //                returnmsg = "100"; //完成
            //            }
            //            else
            //            {
            //                string appid = "";
            //                appid = item.app_id;
            //                returnmsg = item.stepstatus.ToString();
            //                APISparkJobModel sparkmodel = new APISparkJobModel
            //                {
            //                    applicationID = item.app_id
            //                };
            //                string strsparkstatus = JsonHelper.SerializeObject(sparkmodel);
            //                log.Info("job json  :" + strsparkstatus);

            //                // string pythonstr = "{\"projName\": \"test_import_all\", \"projStep\": \"getServerFolder\", \"projID\": \"1\"}";
            //                byte[] bytespark = Encoding.GetEncoding("utf-8").GetBytes(strsparkstatus);

            //                //參數編成 Base64 字串
            //                string JsonServer = Convert.ToBase64String(bytespark);

            //                APIModel apiModel = new APIModel
            //                {
            //                    jsonBase64 = JsonServer
            //                };

            //                string strapi = JsonHelper.SerializeObject(apiModel);
            //                //var apirestult=HttpHelper.PostUrl("getServerFolder", "{\"jsonBase64\":\"eyJwcm9qTmFtZSI6ICJ0ZXN0X2ltcG9ydF9hbGwiLCAicHJvalN0ZXAiOiAiZ2V0U2VydmVyRm9sZGVyIiwgInByb2pJRCI6ICIxIn0=\"}");                
            //                var apirestult = HttpHelper.PostUrl("getSparkJobStatusB64", strapi);
            //                if (apirestult != "")
            //                {
            //                    JObject apiresultJsobj = JObject.Parse(apirestult);
            //                    string apibase641 = apiresultJsobj["jsonBase64"].ToString();
            //                    var jsapiresults = Encoding.UTF8.GetString(Convert.FromBase64String(apibase641));
            //                    log.Info("web api return json :" + jsapiresults);
            //                    if (jsapiresults.Length > 2)
            //                    {
            //                        JObject apidecode = JObject.Parse(jsapiresults);
            //                        //"{\"Start-Time\": \"1550301766251\", \"Application-Id\": \"application_1550199357248_0040\", \"Final-State\": \"SUCCEEDED\", 
            //                        //\"State\": \"FINISHED\", \"Progress\": \"100%\", \"Finish-Time\": \"1550301786413\"}"
            //                        string apistatus = apidecode["Final-State"].ToString();
            //                        if (apistatus == "SUCCEEDED")
            //                        {
            //                            string process = apidecode["Progress"].ToString().Replace("%", "");
            //                            //更新SparkMan 狀態與Project 狀態

            //                            var sparkupdate = psService.UpdateProjectSparkStauts(item.pspark_id, item.app_id, process);
            //                            if (sparkupdate)
            //                            {
            //                                //project
            //                                if (item.step == "ImportFile")
            //                                {
            //                                    var prostatus = mydbhelper.UpdateProjectStauts(item.project_id, 3, "資料集屬性判定");
            //                                    if (prostatus)
            //                                    {
            //                                        //ViewData["ProjectStep"] = "2";
            //                                    }
            //                                }
            //                                else if (item.step == "Gen")
            //                                {
            //                                    var prostatus = mydbhelper.UpdateProjectStauts(item.project_id, 7, "去識別化與風險設定處理");
            //                                    if (prostatus)
            //                                    {
            //                                        //ViewData["ProjectStep"] = "2";
            //                                    }
            //                                }
            //                                else if (item.step == "kchecking_async")
            //                                {
            //                                    var prostatus = mydbhelper.UpdateProjectStauts(item.project_id, 7, "去識別化與風險設定處理");
            //                                    if (prostatus)
            //                                    {

            //                                        //delete ProjecteJobStatus
            //                                    }
            //                                }
            //                                else if (item.step == "risk")
            //                                {
            //                                    var prostatus = mydbhelper.UpdateProjectStauts(item.project_id, 10, "可用性感興趣欄位選定");
            //                                    if (prostatus)
            //                                    {

            //                                        //delete ProjecteJobStatus
            //                                    }
            //                                }
            //                                else if (item.step == "MLutility")
            //                                {
            //                                    var prostatus = mydbhelper.UpdateProjectStauts(item.project_id, 12, "報表查看");
            //                                    if (prostatus)
            //                                    {

            //                                        //delete ProjecteJobStatus
            //                                    }
            //                                }
            //                                else if (item.step == "exportfile")
            //                                {
            //                                    var prostatus = mydbhelper.UpdateProjectStauts(item.project_id, 15, "去識別化完成");
            //                                    if (prostatus)
            //                                    {

            //                                        //delete ProjecteJobStatus
            //                                    }
            //                                }
            //                            }
            //                            else
            //                            {
            //                                //spark update error
            //                            }
            //                        }
            //                    }
            //                }
            //            }
            //        }
            //        catch (Exception ex)
            //        {
            //            string errormsg = ex.Message.ToString();
            //            log.Error("GetNotification Error :" + errormsg);
            //        }

            //        pname_cht = item.project_cht;
            //        step = item.step;
            //        not_ntml += "<li class=\"notification_dropdown_item\">" + "<img src=\"/images/noti_light.png\">" +
            //                    "<div class=\"text\"><p>" + item.project_cht + "  " + item.step + "</p><div class=\"time\">" + item.createtime.ToString("MM-dd") + "</div></div></li>";
            //    }
            //}
            #endregion

            //add appStatus
            //var lstappStatus = mydbhelper.SelectProjectAppStatus();
            if (jobcount.Count > 0)
            {
                sparkjobcount = jobcount.Count;
                jobcount_num = jobcount_num - jobcount.Count;
                foreach (var items in jobcount)
                {
                    pname_cht = items.project_cht;

                    not_ntml += "<li class=\"notification_dropdown_item\">" + "<img src=\"/images/noti_light.png\">" +
                                "<div class=\"text\"><p>" + pname_cht + "  " + items.Application_Name + "</p><div class=\"time\">" + items.statustime.ToString("yyyy-MM-dd HH:mm:ss") + "</div></div></li>";
                }
            }

            if (jobstatusresult.Count > 0)
            {
                //sparkjobcount += jobstatusresult.Count;
                //sparkjobcount = sparkjobcount + lstappStatus.Count;
                int x = 0;
                foreach (var items in jobstatusresult)
                {
                    pname_cht = "";
                    pname_cht = items.project_cht;
                    if (x < jobcount_num)
                    {
                        not_ntml += "<li class=\"notification_dropdown_item read\">" + "<img src=\"/images/noti_light.png\">" +
                                    "<div class=\"text\"><p>" + pname_cht + "  " + items.Application_Name + "</p><div class=\"time\">" + items.statustime.ToString("yyyy-MM-dd HH:mm:ss") + "</div></div></li>";
                    }
                    x++;
                }
            }

            //if (sparkjobcount != 0)
            //{
            string final_html = "<li class=\"notification_dropdown_item\">" + _localizer.Text.notification + "</li>" + not_ntml;
            returnmsg = sparkjobcount + "*" + final_html;
            //}
            //組成 json 

            return returnmsg;
        }

        [HttpGet("UpdateStatsRead")]
        public bool UpdateStatsRead()
        {
            bool isUpdate = false;
            try
            {
                var jobstatusresult = mydbhelper.UpdateReadStauts();
                if (jobstatusresult)
                    isUpdate = true;
            }
            catch (Exception ex)
            {
                log.Error("UpdateStatsRead Exception :" + ex.Message);
            }
            return isUpdate;
        }

        [HttpGet("TestConnection")]
        public string TestConnection(string testname)
        {
            try
            {
                log.Info("TestConnection :" + testname);
                return "Y";
            }
            catch (Exception ex)
            {
                return "N";
            }
        }

        [HttpGet("SendMLutility")]
        public bool SendMLutility(string pid, string pname, string fname, string targernm)
        {
            bool isUpdate = false;
            log.Info("SendMLutility API");
            log.Info("SendMLutility API targetName :" + targernm);
            var ps_id = "";

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
                //select projeName pro_tb finaltable

                var lstSampleTB = proj_Service.SelectProjSampleTB(pid);
                if (lstSampleTB.Count > 0)
                {
                    foreach (var item in lstSampleTB)
                    {
                        var col_cht = item.pro_col_cht;
                        var col_en = item.pro_col_en;
                        var col_cht_arr = col_cht.Split(',');
                        var col_en_arr = col_en.Split(',');
                        var newtarget = "";
                        for (int z = 0; z < tager_arr.Length; z++)
                        {
                            for (int b = 0; b < col_cht_arr.Length; b++)
                            {
                                if (tager_arr[z] == col_cht_arr[b])
                                {
                                    newtarget += col_en_arr[b].ToString() + ",";
                                }
                            }
                        }

                        if (newtarget.Length > 0)
                        {
                            newtarget = newtarget.Substring(0, newtarget.Length - 1);
                        }
                        var newtarget_arr = newtarget.Split(',');
                        //JSON
                        MLDataModelAPI mlsyncapi = new MLDataModelAPI
                        {
                            userID = "1",
                            projID = pid,
                            projName = pname,
                            rawTbl = item.pro_tb,
                            deIdTbl = item.finaltblName,
                            targetCols = newtarget_arr

                        };
                        ps_id = item.ps_id.ToString();
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
                        log.Info("MLutility_async  Base64 :" + strapi);
                        //var apirestult=HttpHelper.PostUrl("getServerFolder", "{\"jsonBase64\":\"eyJwcm9qTmFtZSI6ICJ0ZXN0X2ltcG9ydF9hbGwiLCAicHJvalN0ZXAiOiAiZ2V0U2VydmVyRm9sZGVyIiwgInByb2pJRCI6ICIxIn0=\"}");                
                        var apirestult = HttpHelper.PostUrl("MLutility_async", strapi);
                        log.Info("MLutility_async return base64:" + apirestult);
                        JObject apiresultJsobj = JObject.Parse(apirestult);
                        // JObject apiresultJsobj = JObject.Parse(apirestult);
                        // JObject apidecode = JObject.Parse(jsapiresults);
                        string apistatus = apiresultJsobj["status"].ToString();
                        if (apistatus == "1")
                        {
                            //update in TargetCol
                            var uptbtarget = proj_Service.UpdateProjectSampleTableTarget(ps_id, pid, targernm);
                            if (uptbtarget)
                            {
                                List<ProjectSparkMan> ojString = new List<ProjectSparkMan>();
                                ProjectSparkMan psman = new ProjectSparkMan
                                {
                                    celery_id = apiresultJsobj["celeryId"].ToString(),
                                    app_id = apiresultJsobj["sparkAppID"].ToString(),
                                    step = "MLutility_async",
                                    stepstatus = 0,
                                    //TODO
                                    //增加欄位 step  用已確認步驟
                                    project_id = int.Parse(pid)
                                };
                                log.Info("celeryID : " + apiresultJsobj["celeryId"].ToString());
                                log.Info("sparkAppID : " + apiresultJsobj["sparkAppID"].ToString());
                                log.Info("step : " + "MLutility");
                                log.Info("stepstatus :0");
                                ojString.Add(psman);
                                var sparkstatus = mydbhelper.InsertSparkStauts(ojString);

                                //更新系統狀態
                                if (sparkstatus)
                                {
                                    var prostatus = mydbhelper.UpdateProjectStauts(int.Parse(pid), 12, "可用性欄位分析中");
                                    if (prostatus)
                                    {
                                        var jobstatus = mydbhelper.UpdateProjectJobStauts(int.Parse(pid), 1, "ML", fname, "MLutility");
                                        if (jobstatus)
                                            return true;
                                        // return true;
                                    }
                                }
                                else
                                {
                                    log.Debug("MLutility_async JOB MAN UPDATE ERROR");
                                    //string errMsg = "-1";
                                    //returnmsg = errMsg;
                                    return true;
                                }
                            }
                        }
                        else
                        {
                            string errMsg = apiresultJsobj["errMsg"].ToString();
                            log.Error("MLutility_async Return Json Error :" + errMsg);
                            //returnmsg = "-2";
                        }
                    }
                }

            }
            catch (Exception ex)
            {
                string errormsg = ex.Message.ToString();
                log.Error("SendMLutility Exception :" + errormsg);

            }
            return isUpdate;
        }

        [HttpGet("SendDeIdRisk")]
        public bool SendDeIdRisk(string pid, string pname)
        {
            bool isUpdate = false;
            string qi_col = "";
            string sa_col = "";
            string colNames = "";
            string tableName = "";
            string dbName = "";
            log.Info("SendDeIdRisk API");

            //log.Info("FileName  :" + fname);

            if (pid == "")
            {
                return false;
            }


            //var tager_arr = targernm.Split(',');
            try
            {
                //select projeName pro_tb finaltable
                List<RiskmainInfoModel> lstrisk = new List<RiskmainInfoModel>();
                var lstSampleTB = proj_Service.SelectProjSampleTB(pid);
                if (lstSampleTB.Count > 0)
                {
                    foreach (var item in lstSampleTB)
                    {
                        string qi_value_cht = item.qi_col;
                        var qi_arr = qi_value_cht.Split(',');
                        string col_cht = item.after_col_cht;
                        string pro_tb = item.pro_tb;
                        string finaltb = item.finaltblName;
                        string dbname = item.pro_db;
                        var encolarr = item.after_col_en.Split(',');
                        var colarr = col_cht.Split(',');
                        for (int i = 0; i < colarr.Length; i++)
                        {
                            for (int x = 0; x < qi_arr.Length; x++)
                            {
                                var qidata = qi_arr[x].Split('-');
                                if (qidata[0] == colarr[i])
                                {
                                    if (qidata[1] == "1")
                                    {
                                        qi_col += encolarr[i] + ",";
                                    }
                                    else if (qidata[1] == "2") //sa
                                    {
                                        sa_col += encolarr[i] + ",";
                                    }
                                    //qi_col += encolarr[i] + ",";
                                }
                            }
                        }

                        if (qi_col.Length > 0)
                            qi_col = qi_col.Substring(0, qi_col.Length - 1);

                        if (sa_col.Length > 0)
                            sa_col = sa_col.Substring(0, sa_col.Length - 1);

                        var qi_col_arr = qi_col.Split(',');
                        var sa_col_arr = sa_col.Split(',');
                        ////JSON
                        RiskmainInfoModel riskinfo = new RiskmainInfoModel
                        {
                            dbname = dbname,
                            pro_tb = pro_tb,
                            final_tb = finaltb,
                            qi = qi_col_arr,
                            sa = sa_col_arr
                        };
                        lstrisk.Add(riskinfo);
                    }


                    string riskmainInfo = JsonHelper.SerializeObject(lstrisk);
                    //var strdataInfo = "[" + kcheckdataInfo + "]";
                    var jarrydataInfo = JArray.Parse(riskmainInfo);

                    RiskDeIdModel riskdeidinfo = new RiskDeIdModel
                    {
                        mainInfo = jarrydataInfo,
                        project_id = pid,
                        projStep = "getRisk",
                        projName = pname,
                        userid = "1"
                    };
                    string serverfolderstr = JsonHelper.SerializeObject(riskdeidinfo);
                    log.Info("getRisk_async :" + serverfolderstr);
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
                    var apirestult = HttpHelper.PostUrl("getRisk_async", strapi);
                    log.Info("getRisk_async return base64:" + apirestult);
                    JObject apiresultJsobj = JObject.Parse(apirestult);
                    // JObject apiresultJsobj = JObject.Parse(apirestult);
                    string state = apiresultJsobj["status"].ToString();
                    if (state != "1")
                    {

                        string errmsg = apiresultJsobj["errMsg"].ToString();
                        log.Error("getRisk_async State Error :" + state);
                        return false;
                    }
                    else
                    {
                        ////更新欄位
                        var up5Data = true;// projService.UpdateProjectSample5DataTarget(int.Parse(pid), pname, targernm);
                        if (up5Data)
                        {
                            var prostatus = mydbhelper.UpdateProjectStauts(int.Parse(pid), 9, "風險評估進行中");
                            if (prostatus)
                                isUpdate = true;
                        }
                        else
                        {
                            isUpdate = false;
                        }
                    }

                }

            }
            catch (Exception ex)
            {
                string errormsg = ex.Message.ToString();
                log.Error("getRisk_async Exception :" + errormsg);

            }
            return isUpdate;
        }

        [HttpGet("CheckSparkJobStatus")]
        public string CheckSparkJobStatus()
        {
            string returnmsg = "";

            //組成 json 
            string strjson = "eyJhcHBsaWNhdGlvbklEIjogImFwcGxpY2F0aW9uXzE1NDU2NDMxMzAxNTRfMDAwNCJ9";
            var jsondecode = Encoding.UTF8.GetString(Convert.FromBase64String(strjson));
            //"{\"applicationID\": \"application_1545643130154_0004\"}"
            return returnmsg;
        }

        [HttpGet("GetSingleTable")]
        public bool GetSingleTable(string pid, string pname, string tablename, string jobname)
        {
            try
            {
                log.Info("WebAPI GetSingleTable");
                log.Info("pid :" + pid);
                log.Info("pname :" + pname);
                log.Info("tablename :" + tablename);
                string selectjob = "single";
                int jobint = 0;
                switch (jobname)
                {
                    case "job1":
                        jobint = 0;
                        break;
                    case "job2":
                        jobint = 1;
                        break;
                    case "job3":
                        jobint = 2;
                        break;
                    case "job4":
                        jobint = 3;
                        break;
                    case "job5":
                        jobint = 4;
                        break;


                }
                var lstproject = mydbhelper.SelectProjectJobStauts(pid, jobint, selectjob);

                if (lstproject.Count > 0)
                {
                    var sparkstatus = mydbhelper.UpdateProjectJobStauts(int.Parse(pid), 0, "single", tablename, jobname);
                    if (sparkstatus)
                        return true;
                }
                else
                {

                    List<ProjectJob> ojString = new List<ProjectJob>();
                    ProjectJob psman = new ProjectJob();
                    psman.project_id = int.Parse(pid);
                    psman.jobrule = jobname;
                    psman.job_tb = tablename;
                    psman.project_jobstatus = 0;
                    psman.jobname = "single";

                    ojString.Add(psman);

                    var sparkstatus = mydbhelper.InsertProjectJobStauts(ojString);
                    if (sparkstatus)
                        return true;

                }
            }
            catch (Exception ex)
            {
                log.Error("GetSingleTable Exception :" + ex.Message);
                return false;
            }
            return false;
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
            return "True";
        }

        [HttpGet("ResetML")]
        public string ResetML(int project_id)
        {
            ////string insertsql = "insert into T_Member(project_name,project_desc,project_path,exoprt_path,projectowner_id,createtime)values('" + pname + "','" + prodesc + "','" + pinput + "','" + poutput + "'," + powner + ",Now());";
            // result = mydbhelper.InsertProject(insertsql);
            log.Info("重設可用性分析 ");

            //mydbhelper.UpdateProjectStatus(project_id,11);
            mydbhelper.ResetML(project_id);
            return "True";
        }
        [HttpGet("ChangePassWd")]
        public int ChangePassWd(string old_pwd, string new_pwd, string userAcc, string userId)
        {
            int isChange = 1;
            try
            {
                var oldpass = "";
                var md5pwd = MD5Str.MD5(old_pwd);
                var memberlst = mService.GetMember(userAcc);
                var newpwd = MD5Str.MD5(new_pwd);
                foreach (var item in memberlst)
                {
                    oldpass = item.Password;
                }
                if (oldpass != md5pwd)
                {
                    isChange = -2;
                }
                else
                {
                    var boolmember = mService.UpdateUserPass(userId, userAcc, newpwd);
                    if (boolmember == false)
                    {
                        isChange = -1;

                    }

                }
            }
            catch (Exception ex)
            {
                log.Error("change Password Error " + ex.Message);
                isChange = -99;
                //return isChange;
            }
            //string insertsql = "insert into T_Member(project_name,project_desc,project_path,exoprt_path,projectowner_id,createtime)values('" + pname + "','" + prodesc + "','" + pinput + "','" + poutput + "'," + powner + ",Now());";
            //var result = mydbhelper.InsertProject(insertsql);
            return isChange;
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

        [HttpPost("GetProjectSampleTable")]
        public string GetProjectSampleTable(int project_id)
        {
            //string insertsql = "insert into T_Member(project_name,project_desc,project_path,exoprt_path,projectowner_id,createtime)values('" + pname + "','" + prodesc + "','" + pinput + "','" + poutput + "'," + powner + ",Now());";
            //var result = mydbhelper.InsertProject(insertsql);
            return "";
        }
        [HttpPost("GetGenStep")]
        public string GetGenStep(string jsonString)
        {
            //HttpHelper.PostUrl("http://140.96.178.114:5999", "Generalization_async", "{\"jsonBase64\":\"eyJwcm9qTmFtZSI6ICJudHVfbWFycmlhZ2VfcHJvamVjdCIsICJwcm9qU3RlcCI6ICJnZXRTZXJ2ZXJGb2xkZXIiLCAicHJvaklEIjogIjEifQ == \"}");

            //string insertsql = "insert into T_Member(project_name,project_desc,project_path,exoprt_path,projectowner_id,createtime)values('" + pname + "','" + prodesc + "','" + pinput + "','" + poutput + "'," + powner + ",Now());";
            //mydbhelper.UpdateProjectStatus(4);
            return "True";
        }

        [HttpGet("GetKChecking")]
        public bool GetKChecking(string pid, string pname, string jobname,string finaltablename)
        {
            log.Info("GetKChecking");
            log.Info("pid :" + pid);
            log.Info("pname :" + pname);
            log.Info("jobname :" + jobname);
            try
            {
                string projstep = "kchecking_one";
                string qi_col = "";
                string colNames = "";
                string tableName = "";
                string dbName = "";
                string keyNames = "";
                string minkvalue = "";
                var lstsingle = GetSingleTable(pid, pname, finaltablename, jobname);
                var lstSampleTB = proj_Service.SelectProjSampleJobTB(pid, jobname);
                // var lstproject = mydbhelper.SelectProjectJobStauts(pid, jobint, selectjob);

                if (lstSampleTB.Count > 0)
                {
                    foreach (var item in lstSampleTB)
                    {
                        colNames = item.after_col_en;
                        string col_cht = item.after_col_cht;
                        string qi_value_cht = item.qi_col;
                        var encolarr = item.after_col_en.Split(',');
                        var colarr = col_cht.Split(',');
                        var keyarrs = item.tablekeycol.Split(',');
                        // keyNames = item.tablekeycol;
                        var qi_arr = qi_value_cht.Split(',');
                        minkvalue = item.minKvalue.ToString();
                        keyNames = "";
                        for (int a = 0; a < keyarrs.Length; a++)
                        {
                            if (keyarrs[a] != "")
                            {
                                for (int z = 0; z < encolarr.Length; z++)
                                {
                                    if (keyarrs[a] == colarr[z])
                                    {
                                        keyNames += encolarr[z] + ",";
                                    }
                                }
                            }
                        }


                        for (int i = 0; i < colarr.Length; i++)
                        {
                            //if (keyNames == colarr[i])
                            //{
                            //    keyNames = encolarr[i];
                            //}
                            for (int x = 0; x < qi_arr.Length; x++)
                            {
                                var qidata = qi_arr[x].Split('-');
                                if (qidata[0] == colarr[i])
                                {
                                    if (qidata[1] == "1")
                                    {
                                        qi_col += encolarr[i] + ",";
                                    }
                                    //qi_col += encolarr[i] + ",";
                                }
                            }
                        }

                        keyNames = keyNames.Substring(0, keyNames.Length - 1);
                        qi_col = qi_col.Substring(0, qi_col.Length - 1);
                        tableName = item.finaltblName;
                        dbName = item.pro_db;
                        //
                        var qi_colarr = qi_col.Split(',');
                        var colNamearr = colNames.Split(',');
                        var keyarr = keyNames.Split(',');
                        KcheckdataInfoModel kdm = new KcheckdataInfoModel
                        {
                            QIcols = qi_colarr,
                            colNames = colNamearr,
                            tableName = tableName,
                            dbName = dbName,
                            keyNames = keyarr
                        };
                        string kcheckdataInfo = JsonHelper.SerializeObject(kdm);
                        var strdataInfo = "[" + kcheckdataInfo + "]";
                        var jarrydataInfo = JArray.Parse(strdataInfo);
                        APIKcheckMainInfoModel kmain = new APIKcheckMainInfoModel
                        {
                            joinType = "inner",
                            kValue = minkvalue,
                            publicTableName = tableName,
                            dataInfo = jarrydataInfo
                        };
                        string kcheckmainInfo = JsonHelper.SerializeObject(kmain);
                        //kcheckmainInfo = kcheckmainInfo.Replace('\\', ' ');
                        //kcheckmainInfo = kcheckmainInfo.Replace('\"', ' ');

                        // string jobnames = "job01";
                        APIKcheckModel kcheckmd = new APIKcheckModel
                        {
                            projID = pid,
                            projStep = projstep,
                            projName = pname,
                            jobName = jobname,
                            kchecking = 1,
                            mainInfo = kmain,
                            userAccount = "deidadmin",
                            userId = "1"
                        };

                        string kcheckstr = JsonHelper.SerializeObject(kcheckmd);
                        kcheckstr = kcheckstr.Replace('\\', ' ');

                        kcheckstr = kcheckstr.Replace(" ", "");
                        log.Info("Kcheck Json String :" + kcheckstr);
                        // string pythonstr = "{\"projName\": \"test_import_all\", \"projStep\": \"getServerFolder\", \"projID\": \"1\"}";
                        byte[] byteServer = Encoding.GetEncoding("utf-8").GetBytes(kcheckstr);

                        //參數編成 Base64 字串
                        string JsonServer = Convert.ToBase64String(byteServer);

                        APIModel apiModel = new APIModel
                        {
                            jsonBase64 = JsonServer
                        };

                        string strapi = JsonHelper.SerializeObject(apiModel);
                        log.Info("Kcheck API String :" + strapi);

                        var apirestult = HttpHelper.PostUrl("kchecking_async", strapi);

                        JObject apiresultJsobj = JObject.Parse(apirestult);
                        string apibase641 = apiresultJsobj["jsonBase64"].ToString();
                        var jsapiresults = Encoding.UTF8.GetString(Convert.FromBase64String(apibase641));
                        log.Info("Kcheck return JsonString :" + jsapiresults);
                        JObject apidecode = JObject.Parse(jsapiresults);
                        string apistatus = apidecode["status"].ToString();
                        if (apistatus == "1")
                        {
                            List<ProjectSparkMan> ojString = new List<ProjectSparkMan>();
                            ProjectSparkMan psman = new ProjectSparkMan
                            {
                                celery_id = apidecode["celeryID"].ToString(),
                                app_id = apidecode["sparkAppID"].ToString(),
                                step = "kchecking_async",
                                stepstatus = 0,
                                //TODO
                                //增加欄位 step  用已確認步驟
                                project_id = int.Parse(pid)
                            };
                            log.Info("celeryID : " + apidecode["celeryID"].ToString());
                            log.Info("sparkAppID : " + apidecode["sparkAppID"].ToString());
                            log.Info("step : " + "kchecking");
                            log.Info("stepstatus :0");
                            ojString.Add(psman);
                            var sparkstatus = mydbhelper.InsertSparkStauts(ojString);

                            //更新系統狀態
                            if (sparkstatus)
                            {
                                var prostatus = mydbhelper.UpdateProjectStauts(int.Parse(pid), 8, "去識別化處理中");
                                if (prostatus)
                                {
                                    var jobstatus = mydbhelper.UpdateProjectJobStauts(int.Parse(pid), 1, "single", tableName, jobname);
                                    if (jobstatus)
                                        return true;
                                    // return true;
                                }
                            }
                            else
                            {
                                log.Debug("KCHECKING JOB MAN UPDATE ERROR");
                                //string errMsg = "-1";
                                //returnmsg = errMsg;
                                return true;
                            }
                        }
                        else
                        {
                            string errMsg = apidecode["errMsg"].ToString();
                            log.Error("GetKChecking Return Json Error :" + errMsg);
                            //returnmsg = "-2";
                        }
                    }

                }
                else
                {
                    return false;
                }

            }
            catch (Exception ex)
            {
                log.Error("GetKChecking exception :" + ex.Message);
            }
            log.Error("Kchecking Json Decode Error");
            return false;
        }


        [HttpGet("InsertJobStatus")]
        public string InsertJobStatus(string jsonString)
        {
            //string insertsql = "insert into T_Member(project_name,project_desc,project_path,exoprt_path,projectowner_id,createtime)values('" + pname + "','" + prodesc + "','" + pinput + "','" + poutput + "'," + powner + ",Now());";
            //var result = mydbhelper.InsertProject(insertsql);
            return "";
        }

        [HttpPost("selectSampleTBColumn")]
        public string selectSampleTBColumn(string project_id)
        {
            //string insertsql = "insert into T_Member(project_name,project_desc,project_path,exoprt_path,projectowner_id,createtime)values('" + pname + "','" + prodesc + "','" + pinput + "','" + poutput + "'," + powner + ",Now());";
            //var result = mydbhelper.InsertProject(insertsql);
            return "";
        }

        [HttpGet("AddMember")]
        public string AddMember(string usracc, string usrpwd, string userdept, string useradmin)
        {
            try
            {
                log.Info("AddMember 建立User 名稱:" + usracc);
                log.Info("AddMember 單位:" + userdept);
                log.Info("AddMember 是否管理員:" + useradmin);


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
                string insertsql = "insert into T_Member(useraccount,username,password,dept_id,isAdmin,createtime)values('" + usracc + "','" + usracc + "','" + pwdmd5 + "','" + userdept + "'," + useradmin + ",Now());";
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
                return "-99";
            }
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
                if (lstmember.Count > 0)
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


    }
}