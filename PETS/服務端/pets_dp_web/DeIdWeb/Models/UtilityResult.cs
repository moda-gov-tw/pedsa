using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;

namespace DeIdWeb.Models
{
    public class UtilityResult
    {
        public int Id { get; set; }
        public int project_id { get; set; }
        public string target_col { get; set; }
        public string select_csv { get; set; }
        public string model { get; set; }
        public string MLresult { get; set; }
        public DateTime createtime { get; set; }
        public DateTime updatetime { get; set; }
    }
}
