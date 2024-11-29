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


    public class gan_report
    {
        public int epsilon { get; set; }
        public List<Rawdata_info> rawdata_info { get; set; }
        public List<Syndata_info> syndata_info { get; set; }
    }
}
