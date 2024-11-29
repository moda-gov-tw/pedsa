using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;

namespace DeIdWeb.Models
{
    public class ProjectJob
    {
        public int pjs_id { get; set; }
        public int project_id { get; set; }
        public int project_jobstatus { get; set; }
        public string jobname { get; set; }
        public string job_tb { get; set; }
        public string jobrule { get; set; }
        public DateTime createtime { get; set; }
        public DateTime? updatetime { get; set; }
    }
}
