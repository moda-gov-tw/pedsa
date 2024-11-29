using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;

namespace DeIdWeb_V2_K.Models
{
    public class ProjectList
    {
        public int project_id { get; set; }
        public int project_status { get; set; }
        public string project_name { get; set; }
        public string project_desc { get; set; }
        public DateTime projecttime { get; set; }
        public string useraccount { get; set; }
        public string project_cht { get; set; }
        public string isML { get; set; }

        //public string projectowner { get; set; }
    }
}
