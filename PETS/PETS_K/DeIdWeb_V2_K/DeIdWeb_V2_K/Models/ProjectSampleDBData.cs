using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;

namespace DeIdWeb_V2_K.Models
{
    public class ProjectSampleDBData
    {
        public int ps_id { get; set; }
        public int project_id { get; set; }
        public string pro_db { get; set; }
        public string pro_tb { get; set; }
        public string pro_col_en { get; set; }
        public string jobname { get; set; }
        public string pro_col_cht { get; set; }
        public DateTime createtime { get; set; }
        public DateTime? updatetime { get; set; }
        public string pro_path { get; set; }
        public int tableCount { get; set; }
        public int tableDisCount { get; set; }
        public int minKvalue { get; set; }
        public string supRate { get; set; }
        public int supCount { get; set; }
        public string finaltblName { get; set; }
        public string gen_qi_settingvalue { get; set; }
        public string qi_col { get; set; }
        public string tablekeycol { get; set; }
        public string after_col_cht { get; set; }
        public string after_col_en { get; set; }
        public string data { get; set; }
        public string kdata { get; set; }
        public string distinctCount { get; set; }
        public string after_col_value { get; set; }
        public string warning_col { get; set; }
        public string k_risk { get; set; }
        public decimal? T1 { get; set; }
        public decimal? T2 { get; set; }
        public decimal? r_value { get; set; }
        public decimal? max_t { get; set; }
    }
}
