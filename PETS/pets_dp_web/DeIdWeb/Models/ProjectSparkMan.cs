using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;

namespace DeIdWeb.Models
{
    public class ProjectSparkMan
    {
        //(@app_id,@celery_id,@project_id,now())";
        public int pspark_id { get; set; }
        public int stepstatus { get; set; }
        public string app_id { get; set; }
        public string celery_id { get; set; }
        public string step { get; set; }
        public string project_name { get; set; }
        public int project_id { get; set; }
        public DateTime createtime { get; set; }
        //public string Email { get; set; }
        public DateTime? updatetime { get; set; }
    }
}
