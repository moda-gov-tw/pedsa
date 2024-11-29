using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;

namespace DeIdWeb.Models
{
    public class Project
    {
        public int Project_id { get; set; }
        public int project_status { get; set; }
        public int Projectowner_id { get; set; }
        public string project_name { get; set; }
        public string Project_desc { get; set; }
        public string Risk_rdata { get; set; }
        public string R1_data { get; set; }
        public int ftaskid { get; set; }
        public int sectaskid { get; set; }
        public string R2_data { get; set; }
        public DateTime Createtime { get; set; }
        public DateTime Updatetime { get; set; }
        public string Project_path { get; set; }
        public string Export_path { get; set; }
        public string downloadpath { get; set; }
        //public string Email { get; set; }
        public int IsAdmin { get; set; }
    }
}
