using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;

namespace DeIdWeb_V2_K.Models
{
    public class ProjectSampleDataModel
    {
        public int id { get; set; }
        public int project_id { get; set; }
        public string dbname { get; set; }
        public string tbname { get; set; }
        public string data { get; set; }
        public DateTime createtime { get; set; }
        public DateTime? updatetime { get; set; }
    }
}
