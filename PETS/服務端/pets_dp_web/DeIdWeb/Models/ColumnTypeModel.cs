using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;

namespace DeIdWeb.Models
{
    public class ColumnTypeModel
    {
        public int Id { get; set; }
        public int project_id { get; set; }
        public string user_id { get; set; }
        public string pro_name { get; set; }
        public string file_name { get; set; }
        public string pro_col_en { get; set; }
        public string pro_col_cht { get; set; }
        public int tableCount { get; set; }
        public string ob_col  { get; set; }
        public string ID_column { get; set; }
        public string pro_col_en_nunique { get; set; }
        public string selectcol { get; set; }
        public string selectcolvalue { get; set; }
        public string corr_col { get; set; }
        public string choose_corr_col { get; set; }
        public double epsilon { get; set; }
        public DateTime createtime { get; set; }
        public DateTime updatetime { get; set; }
    }
}
