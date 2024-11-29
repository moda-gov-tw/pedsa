using Newtonsoft.Json.Linq;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;

namespace DeIdWeb_V2_K.Models
{
    public class K_ReportModel
    {
    }
    public class DataStructure
    {
        public string col_name { get; set; }
        public string col_setting { get; set; }
        public string col_process { get; set; }
    }

    public class DatasetInfo
    {
        public string ds_name { get; set; }
        public string ds_suprate { get; set; }
        public string risk_k { get; set; }
        public int ds_count { get; set; }
        public int k_ds_count { get; set; }
        public int k_sup_count { get; set; }
    }

    public class Warnning_col
    {
        public string warnning_col { get; set; }
        public int warnning_count { get; set; }
    }

    public class k_report
    {
        public DatasetInfo datasetInfo { get; set; }
        public List<DataStructure> dataStructure { get; set; }
        public List<Warnning_col> warnning_col { get; set; }
    }


}
