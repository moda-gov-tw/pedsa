using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;

namespace DeIdWeb.Models
{
    public class ProjectNotification
    {
        public int tgid { get; set; }
        public int project_id { get; set; }
        public int isRead { get; set; }
        public int percentage { get; set; }
        public int projectowner_id { get; set; }
        public string project_name { get; set; }
        public DateTime gan_time { get; set; }
        public string project_cht { get; set; }
        public string pro_name { get; set; }
        public string file_name { get; set; }
        public string jobname { get; set; }
        public string return_result { get; set; }
        public DateTime statustime { get; set; }
    }
}
