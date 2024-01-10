using System;
using System.Collections.Generic;

namespace DeIdWeb.Models
{
    public class GanReportModel
    {

    }


    public class Rawdata_info
    {
        public string col_name { get; set; }
        public string col_type { get; set; }
        public object col_value { get; set; }
    }

    public class ColValue
    {
        public double Min { get; set; }
        public double Max { get; set; }
        public double Mean { get; set; }
        public double Median { get; set; }
        public double Std { get; set; }
    }

    public class stringValue
    {
        public string col_value { get; set; }
        public int col_count { get; set; }
        
    }

    public class Syndata_info
    {
        public string col_name { get; set; }
        public string col_type { get; set; }
        public object col_value { get; set; }
    }

    public class Dpdata_info
    {
        public int project_id { get; set; }
        public string project_name { get; set; }
        public string project_eng { get; set; }
        public string project_env { get; set; }
        public string jobname { get; set; }
        public string project_step { get; set; }
        public string percentage { get; set; }
        public string logcontent { get; set; }
        public string useraccount { get; set; }
        public DateTime createtime { get; set; }
        public DateTime? updatetime { get; set; }
        public string processtime { get; set; }
      
    }


    public class gan_report
    {
        public List<Rawdata_info> rawdata_info { get; set; }
        public List<Syndata_info> syndata_info { get; set; }
    }

    public class dp_joblog
    {
        public int status { get; set; }
        public string msg { get; set; }

        public List<Dpdata_info> dataInfo { get; set; }
    }
}
