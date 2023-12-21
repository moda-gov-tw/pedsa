using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;

namespace DeIdWeb.Models
{
    public class ProjectStatus
    {
        public int ps_id { get; set; }
        public int project_id { get; set; }
        public int project_status { get; set; }
        public string statusname { get; set; }
        public DateTime createtime { get; set; }
        public DateTime? updatetime { get; set; }
    }
}
