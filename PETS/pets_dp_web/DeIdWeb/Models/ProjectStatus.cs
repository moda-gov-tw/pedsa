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
        public string project_name { get; set; }
        public string project_eng { get; set; }
        public string project_env { get; set; }
        public string jobname { get; set; }
        public string project_step { get; set; }
        public string percentage { get; set; }
        public string logcontent { get; set; }
        public string useraccount { get; set; }
        public string processtime { get; set; }
        public DateTime createtime { get; set; }
        public DateTime? updatetime { get; set; }
    }
}
