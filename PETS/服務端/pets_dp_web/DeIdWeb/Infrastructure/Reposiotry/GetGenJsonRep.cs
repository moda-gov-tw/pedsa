using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using log4net;

namespace DeIdWeb.Infrastructure.Reposiotry
{
    public class GetGenJsonRep
    {
        private ILog log = LogManager.GetLogger(Startup.repository.Name, typeof(GetGenJsonRep));

        private string GetAPISelectName(string selectvalue)
        {
            string getQiSelectName = "";
            string apiName = "";
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
                    apiName = "getGenAddress";
                    break;
                case "2":
                    getQiSelectName = "日期";
                    apiName = "getGenDate";
                    break;
                case "3":
                    getQiSelectName = "擷取字串";
                    apiName = "getGenString";
                    break;
                case "4":
                    getQiSelectName = "數字大區間";
                    apiName = "getGenNumLevel";
                    break;
                case "5":
                    getQiSelectName = "數字小區間";
                    apiName = "getGenNumLevel";
                    break;
                case "6":
                    getQiSelectName = "數字區間含上下界";
                    apiName = "getGenNumLevelMinMax";
                    break;
                case "7":
                    getQiSelectName = "不處理";
                    break;
                
            }
            log.Info("概化設定值 :"+selectvalue);
            log.Info("概化設定內容 :"+getQiSelectName);
            log.Info("概化設定API :"+apiName);
            return apiName;
        }

        //private string getAPILevel()
        private string GetQiSelectNameLevel2(string selectvalue, string selectlevel2)
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
                        
                        case "大道、路、街":
                            apilevel = "4";
                            break;
                        case "段":
                            apilevel = "5";
                            break;
                        case "巷":
                            apilevel = "6";
                            break;
                        case "弄":
                            apilevel = "7";
                            break;
                        case "衖":
                            apilevel = "8";
                            break;
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
                            apilevel = "Y";
                            break;
                        case "民國年+月":
                            apilevel = "Mo";
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
                    var updown = selectlevel2.Replace('#',',');
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

        public string GetGenJsonAPI(string pid, string prostep, string projectName, string col_en, string col_cht, string tb,string tbname, string qi_value,string gen_qi_value)
        {
            string genJson = "";
            try
            {
                log.Info("GetGenJsonAPI ");
                log.Info("pid :" + pid);
                log.Info("prostep :" + prostep);
                log.Info("projectName :" + projectName);
                log.Info("col_en :" + col_en);
                log.Info("col_cht :" + col_cht);
                 log.Info("qi_value :" + qi_value);
                log.Info("gen_qi_value :" + gen_qi_value);
                var col_en_array = col_en.Split(',');
                var col_cht_array = col_cht.Split(',');
                var col_qi_array = qi_value.Split(',');
                var col_gentb_arr = gen_qi_value.Split('|');
                for(int b=0;b<col_gentb_arr.Length;b++)
                {
                    if(col_gentb_arr[b]!="")
                    {
                        var col_gen_array = col_gentb_arr[b].Split('*');
                        var tbnm = col_gen_array[0];
                        var col_gen_level1 = col_gen_array[1];
                        var col_gen_level2 = col_gen_array[2];
                       
                        log.Info("tbname :" + tbnm);

                        var gen_level1 = col_gen_level1.Split(',');
                        var gen_level2 = col_gen_level2.Split(',');
                        string genjsoncol = "\"{0}\":{\"colName\":\"{1}\",\"apiName\":\"{2}\",\"userRule\":\"{3}\"},";
                        string finalgenjsoncol = "";
                        for (int i = 0; i < col_cht_array.Length; i++)
                        {   //"5,7,請選擇,請選擇,6,6,請選擇*十歲區間,已上傳,,,50區間,100區間,"
                            for (int x = 0; x < col_qi_array.Length; x++)
                            {
                                var qi_item = col_qi_array[x].Split(',');
                                var qi_item_array = qi_item[0].Split('-');
                                if (col_cht_array[i] == qi_item_array[0])
                                {
                                    if (gen_level1[x] != "請選擇" || gen_level1[x] != "不處理")
                                    {
                                        if (gen_level1[x] == "6")
                                        {
                                            log.Info("tbname 資料及名稱 :"+qi_item_array[0]);
                                            var apiname = GetAPISelectName(gen_level1[x]);
                                            var userRule = GetQiSelectNameLevel2(gen_level1[x], gen_level2[x]);
                                            string coltb = "col_" + (i + 1).ToString();
                                            //genjsoncol = String.Format(genjsoncol,coltb,col_en_array[i].ToString(),apiname,userRule);
                                            genjsoncol = "\"" + coltb + "\":{\"colName\":\"" + col_en_array[i].ToString() + "\",\"apiName\":\"" + apiname + "\",\"userRule\":\"" + userRule + "\"},";

                                        }
                                        else
                                        {
                                            var apiname = GetAPISelectName(gen_level1[x]);
                                            var userRule = GetQiSelectNameLevel2(gen_level1[x], gen_level2[x]);
                                            string coltb = "col_" + (i + 1).ToString();
                                            //genjsoncol = String.Format(genjsoncol,coltb,col_en_array[i].ToString(),apiname,userRule);
                                            genjsoncol = "\"" + coltb + "\":{\"colName\":\"" + col_en_array[i].ToString() + "\",\"apiName\":\"" + apiname + "\",\"userRule\":\"" + userRule + "\"},";
                                        }
                                            finalgenjsoncol += genjsoncol;
                                      
                                    }
                                }


                            }
                        }
                        finalgenjsoncol = finalgenjsoncol.Substring(0, finalgenjsoncol.Length - 1);
                        var newgenjsontb = "\"" + tb + "\":{\"tblName\":\"" + tbname + "\",\"col_en\":\"" + col_en + "\",\"colInfo\":{" + finalgenjsoncol + "}";
                        // string finaljson = String.Format(genjsontb,tb,tbname,col_en,finalgenjsoncol);
                         genJson = newgenjsontb;
                        log.Info("GetGenJsonAPI return Json Str :" + genJson);
                    }
                }
               
                
            }
            catch(Exception ex)
            {
                log.Error("GetGenJsonAPI Exception :"+ex.Message);
            }
            
            return genJson;
        }
    }
}
