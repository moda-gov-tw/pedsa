using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;

namespace DeIdWeb_V2_K.Models
{
    public class RiskDataModel
    {
        public int id { get; set; }
        public int project_id { get; set; }
        public string project_name { get; set; }
        public string dbname { get; set; }
        public string tblname { get; set; }
        public decimal r1 { get; set; }
        public decimal r2 { get; set; }
        public decimal r3 { get; set; }
        public decimal r4 { get; set; }
        public decimal r5 { get; set; }
        public string rs5 { get; set; }
        public string rs1 { get; set; }
        public string rs2 { get; set; }
        public string rs3 { get; set; }
        public string rs4 { get; set; }
    }
}
