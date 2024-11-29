using log4net;
using Microsoft.Extensions.Configuration;
using System;
using System.IO;
using System.Linq;
using System.Text;
using System.Text.RegularExpressions;

namespace DeIdWeb_V2_K.Infrastructure.Reposiotry
{
    public class GenSettingRandomData
    {
        public static IConfiguration Configuration { get; set; }
        public GenSettingRandomData()
        {
            var builder = new ConfigurationBuilder()
            .SetBasePath(Directory.GetCurrentDirectory())
            .AddJsonFile("appsettings.json");
            Configuration = builder.Build();

        }

        private ILog log = LogManager.GetLogger(Startup.repository.Name, typeof(GenSettingRandomData));
        public string SettingQIAddress(string data, string datalevel, string datalevel2)
        {
            log.Info("地址");
            log.Info(data);
            log.Info(datalevel);
            log.Info(datalevel2);
            string str_address1 = null;
            string str_address2 = null;
            string str_address3 = null;
            var stringBuilder = new StringBuilder();
            var finaldata = "";
            //readConfig
            //string data = "新北市內湖區港前路3段128號";
            try
            {

                // string str_address0 = Configuration["GenAddress"];
                str_address1 = Configuration["GenAddress:鎮"];
                str_address2 = "阿里 | 八里 | 萬里 | 后里 | 大里 | 佳里";
                str_address3 = Configuration["GenAddress:路"];
                int x = 0;

                while (x < 1)
                {

                    switch (datalevel2)
                    {
                        case "1": //直轄市
                            log.Info("Case 1");
                            try
                            {
                                string City5pattern = @"^([臺台]北市|新北市|桃園市|[臺台]中市|[臺台]南市|高雄市)(.*)";
                                Match isleve1Match1 = Regex.Match(data, City5pattern);
                                if ((!data.Contains("市")) && (!data.Contains("縣")) && (!isleve1Match1.Success))
                                {
                                    x += 1;
                                    return null;
                                }

                                bool ischeck1 = data.Contains("市");
                                if (data.Contains("市"))
                                {
                                    var dataIndex = data.IndexOf("市");
                                    log.Info("Case 1 dataIndex :" + dataIndex + 1);
                                    finaldata = data.Substring(0, dataIndex + 1);
                                    return finaldata;
                                }
                                else if (data.Contains("縣"))
                                {
                                    bool ischeck1_1 = data.Contains("縣");
                                    if (ischeck1_1)
                                    {
                                        var dataIndex = data.IndexOf("縣");
                                        log.Info("Case 1_1 dataIndex :" + dataIndex + 1);
                                        finaldata = data.Substring(0, dataIndex + 1);
                                    }
                                    else
                                    {
                                        log.Info("Case 1_2 dataIndex 沒有市也沒有縣");
                                        finaldata = data;
                                    }
                                    return finaldata;
                                }
                                else if (isleve1Match1.Success && data.Contains("市"))
                                {
                                    var dataIndex = data.IndexOf("市");
                                    log.Info("Case 1 dataIndex :" + dataIndex + 1);
                                    finaldata = data.Substring(0, dataIndex + 1);
                                    return finaldata;
                                }
                                else
                                {
                                    log.Info("無五都，無縣市");
                                    x += 1;
                                    finaldata = data;
                                    return finaldata;
                                }
                            }
                            catch (Exception ex)
                            {
                                log.Error("target 1 exception :" + ex.Message);
                                return null;
                            }
                            x = +1;


                            break;
                        case "2":  //縣轄市 "鄉、鎮、縣轄市、區
                            string Patternlelve2 = @"^(.*)(竹北市|苗栗市|頭份市|彰化市|員林市|南投市|斗六市|太保市|朴子市|屏東市|宜蘭市|花蓮市|[臺台]東市|馬公市)(.*)";
                            string Patternlelve2_1 = @"^(.*)(區|鎮|鄉)(.*)";
                            string exceptionPattern = @"^(.*)(" + str_address1 + ")(.*)";
                            char ch = '鎮';

                            int num_1 = data.Count(f => (f == ch));
                            Match isleve2Match1 = Regex.Match(data, Patternlelve2);
                            Match isleve2Match2 = Regex.Match(data, Patternlelve2_1);
                            Match isleve2Match3 = Regex.Match(data, exceptionPattern);
                            try
                            {
                                if ((isleve2Match2.Success) && (data.Contains("鄉")))
                                { /*確認地址裡面有鄉*/
                                    int end_point = data.IndexOf("鄉"); /*從前往後找到鄉的index並將地址擷取到該位置*/
                                    finaldata = data.Substring(0, end_point + 1);
                                }
                                else if ((isleve2Match2.Success) && (data.Contains("鎮")))
                                {
                                    // 如果鎮只有一個, 且沒有例外
                                    if ((num_1 == 1) && (!isleve2Match3.Success))
                                    {
                                        int end_point = data.IndexOf("鎮");/*從前往後找鎮*/
                                        finaldata = data.Substring(0, end_point + 1);
                                    }
                                    // 如果鎮超過一個, 且包含例外
                                    else if ((num_1 > 1) && (isleve2Match3.Success))
                                    {
                                        int end_point = data.IndexOf("鎮");/*從後往前找鎮*/
                                        finaldata = data.Substring(0, end_point + 1);
                                    }
                                }
                                else if ((isleve2Match2.Success) && (data.Contains("區")))
                                {
                                    int end_point = data.IndexOf("區");/*從前往後找區*/
                                    finaldata = data.Substring(0, end_point + 1);
                                }
                                else if ((isleve2Match2.Success) && (data.Contains("市")))
                                {
                                    int end_point = data.IndexOf("市");/*從前往後找市*/
                                    finaldata = data.Substring(0, end_point + 1);
                                }
                            }
                            catch (Exception ex)
                            {
                                log.Error("target 2 exception :" + ex.Message);
                                return null;
                            }

                            if (finaldata != null && finaldata != "")
                            {
                                x += 1;
                                return finaldata;
                            }
                            else
                            {
                                datalevel2 = "1";
                            }
                            break;
                        case "3": // "村、里"
                            char ch1 = '里';
                            int num_2 = data.Count(f => (f == ch1));
                            string Patternlelve3 = @"^(.*)(村|里)(.*)";
                            Match isleve3Match1 = Regex.Match(data, Patternlelve3);
                            string exceptionPattern2 = @"^(.*)(" + str_address2 + ")(.*)";
                            Match isleve3Match2 = Regex.Match(data, exceptionPattern2);
                            try
                            {
                                if ((isleve3Match1.Success) && (data.Contains("村")))
                                { /*確認地址裡面有鄉*/
                                    int end_point = data.IndexOf("村"); /*從前往後找到鄉的index並將地址擷取到該位置*/
                                    finaldata = data.Substring(0, end_point + 1);
                                }
                                else if ((isleve3Match1.Success) && (data.Contains("里")))
                                {
                                    if ((num_2 == 1) && (!isleve3Match1.Success))
                                    {
                                        int end_point = data.IndexOf("里"); /*由前往後找里的index，並將地址擷取到該index*/
                                        finaldata = data.Substring(0, end_point + 1);
                                    }
                                    // 如果里超過一個, 且包含例外
                                    else if ((num_2 > 1) && (isleve3Match2.Success))
                                    {
                                        int end_point = data.IndexOf("里");/*由後往前找里的index，並將地址擷取到該index*/
                                        finaldata = data.Substring(0, end_point + 1);
                                    }
                                }
                            }
                            catch (Exception ex)
                            {
                                log.Error("target 3 exception :" + ex.Message);
                                return null;
                            }
                            if (finaldata != null && finaldata != "")
                            {
                                x += 1;
                                return finaldata;
                            }
                            else
                            {
                                datalevel2 = "2";
                            }
                            break;
                        case "4": //鄰
                            try
                            {

                                if (data.Contains("鄰"))
                                {
                                    var dataIndex = data.IndexOf("鄰");
                                    log.Info("Case 4 dataIndex :" + dataIndex);
                                    finaldata = data.Substring(0, dataIndex + 1);
                                }
                            }
                            catch (Exception ex)
                            {
                                log.Error("target 4 exception :" + ex.Message);
                                return null;
                            }

                            if (finaldata != null && finaldata != "")
                            {
                                x += 1;
                                return finaldata;
                            }
                            else
                            {
                                datalevel2 = "3";
                            }

                            break;
                        case "5": // "大道|路|街":
                            char ch2 = '路';
                            int num_3 = data.Count(f => (f == ch2));
                            string Patternlelve5 = @"^(.*)(大道|路|街)(.*)";
                            Match isleve5Match1 = Regex.Match(data, Patternlelve5);
                            string Patternlelve51 = @"^(.*)(" + str_address3 + ")(.*)";
                            Match isleve5Match2 = Regex.Match(data, Patternlelve51);
                            try
                            {
                                if ((isleve5Match1.Success) && (data.Contains("街")))
                                { /*確認地址裡面有街*/
                                    int end_point = data.IndexOf("街"); /*從前往後找到鄉的index並將地址擷取到該位置*/
                                    finaldata = data.Substring(0, end_point + 1);
                                }
                                else if ((isleve5Match1.Success) && (data.Contains("路")))
                                {
                                    if ((num_3 == 1) && (!isleve5Match2.Success))
                                    {
                                        int end_point = data.IndexOf("路"); /*由前往後找里的index，並將地址擷取到該index*/
                                        finaldata = data.Substring(0, end_point + 1);
                                    }
                                    // 如果里超過一個, 且包含例外
                                    else if ((num_3 > 1) && (isleve5Match2.Success))
                                    {
                                        int end_point = data.IndexOf("路");/*由後往前找里的index，並將地址擷取到該index*/
                                        finaldata = data.Substring(0, end_point + 1);
                                    }
                                }
                                else if ((isleve5Match1.Success) && (data.Contains("大道")))
                                {
                                    int end_point = data.IndexOf("大道");/*由後往前找里的index，並將地址擷取到該index*/
                                    finaldata = data.Substring(0, end_point + 2);
                                }
                            }
                            catch (Exception ex)
                            {
                                log.Error("target 5 exception :" + ex.Message);
                                return null;
                            }

                            if (finaldata != null && finaldata != "")
                            {
                                x += 1;
                                return finaldata;
                            }
                            else
                            {
                                datalevel2 = "4";
                            }

                            break;
                        case "6": //"巷":
                            try
                            {
                                bool ischeck4 = data.Contains("段");
                                if (ischeck4)
                                {
                                    var dataIndex = data.IndexOf("段");
                                    log.Info("Case 6 dataIndex :" + dataIndex);
                                    finaldata = data.Substring(0, dataIndex + 1);
                                }

                            }
                            catch (Exception ex)
                            {
                                log.Error("target 6 exception :" + ex.Message);
                                return null;
                            }
                            if (finaldata != null && finaldata != "")
                            {
                                x += 1;
                                return finaldata;
                            }
                            else
                            {
                                datalevel2 = "5";
                            }
                            break;
                        case "7": // "衖"
                            try
                            {
                                bool ischeck4 = data.Contains("巷");
                                if (ischeck4)
                                {
                                    var dataIndex = data.IndexOf("巷");
                                    log.Info("Case 7 dataIndex :" + dataIndex);
                                    finaldata = data.Substring(0, dataIndex + 1);
                                }

                            }
                            catch (Exception ex)
                            {
                                log.Error("target 7 exception :" + ex.Message);
                                return null;
                            }
                            if (finaldata != null && finaldata != "")
                            {
                                x += 1;
                                return finaldata;
                            }
                            else
                            {
                                datalevel2 = "6";
                            }
                            break;
                        case "8":  //"號"
                            try
                            {
                                bool ischeck4 = data.Contains("弄");
                                if (ischeck4)
                                {
                                    var dataIndex = data.IndexOf("弄");
                                    log.Info("Case 8 dataIndex :" + dataIndex);
                                    finaldata = data.Substring(0, dataIndex + 1);
                                }

                            }
                            catch (Exception ex)
                            {
                                log.Error("target 8 exception :" + ex.Message);
                                return null;
                            }
                            if (finaldata != null && finaldata != "")
                            {
                                x += 1;
                                return finaldata;
                            }
                            else
                            {
                                datalevel2 = "7";
                            }
                            break;
                        case "9":  //"號"
                            try
                            {
                                bool ischeck4 = data.Contains("號");
                                if (ischeck4)
                                {
                                    var dataIndex = data.IndexOf("號");
                                    log.Info("Case 9 dataIndex :" + dataIndex);
                                    finaldata = data.Substring(0, dataIndex + 1);
                                }

                            }
                            catch (Exception ex)
                            {
                                log.Error("target 9 exception :" + ex.Message);
                                return null;
                            }
                            if (finaldata != null && finaldata != "")
                            {
                                x += 1;
                                return finaldata;
                            }
                            else
                            {
                                datalevel2 = "8";
                            }
                            break;

                    }
                }

            }
            catch (Exception ex)
            {
                log.Error("地址概化 exception  :" + ex.Message);
                return null;
            }
            return finaldata;
            //   return fin
        }

        public string SettingQIDate(string data, string datalevel)
        {

            var stringBuilder = new StringBuilder();

            return stringBuilder.ToString();

        }

        public string SettingQINumberLevel(string data, string datalevel, string datalevel2)
        {
            var doubleData = double.Parse(data);
            int mathData = (int)doubleData;
            int level2 = int.Parse(datalevel2);
            int S = mathData / level2;

            log.Info("小區間");
            log.Info(data);
            log.Info(S.ToString());
            int finaldata = S * level2;
            return finaldata.ToString();

        }

        public string SettingQINumberMaxMin(string data, string datalevel, int min, int max)
        {

            var doubleData = double.Parse(data);
            int mathData = (int)doubleData;
            int level2 = int.Parse(datalevel);
            int final = 0;
            int finaldata = 0;
            if (mathData > max)
            {
                mathData = max;
                finaldata = mathData;
            }
            else if (mathData < min)
            {
                mathData = min;
                finaldata = mathData;
            }
            else
            {

                final = mathData / level2;
                finaldata = final * level2;
                if(finaldata< min)
                {
                    finaldata = min;
                }
                else if (finaldata > max)
                {
                    finaldata = max;
                }

            }


            return finaldata.ToString();


        }
    }
}
