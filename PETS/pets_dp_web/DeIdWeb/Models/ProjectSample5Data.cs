using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;

namespace DeIdWeb.Models
{
    public class ProjectSample5Data
    {
        public int id { get; set; }
        public int project_id { get; set; }
        public int ftaskid { get; set; }
        public int dp_id { get; set; }
        public int sectaskid { get; set; }
        public string user_id { get; set; }
        public string pro_name { get; set; }
        public string file_name { get; set; }
        public string data { get; set; }
        public string select_colNames { get; set; }
        public string selectcol { get; set; }
        public string selectcolvalue { get; set; }
        public string pro_col_en_nunique { get; set; }
        public string targetCols { get; set; }
        public string ID_Column { get; set; }
        public DateTime createtime { get; set; }
        public DateTime? updatetime { get; set; }
        public string project_name { get; set; }
        public string pro_col_cht { get; set; }
        public string pro_col_en { get; set; }
        public string tableCount { get; set; }
        public string ob_col { get; set; }
        public string select_data { get; set; }
        
    }
}
