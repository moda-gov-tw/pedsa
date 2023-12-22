using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;

namespace DeIdWeb.Models
{
    public class GanStatusModel
    {
        public int Id { get; set; }
        public int project_id { get; set; }
        public int isRead { get; set; }
        public string user_id { get; set; }
        public string pro_name { get; set; }
        public string file_name { get; set; }
        public string jobname { get; set; }
        public DateTime Createtime { get; set; }
        public DateTime Updatetime { get; set; }
    }
}
