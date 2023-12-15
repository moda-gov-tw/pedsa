using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;


namespace DeIdWeb_V2_K.Models
{
    public class SystemLogModel
    {
        public string Id { get; set; }
        public int member_id { get; set; }
        public string username { get; set; }
        public DateTime logtime { get; set; }
        public int logtype { get; set; }
        public string logtype_name { get; set; }
        public string logstep { get; set; }
        public string logcontent { get; set; }
    }
}
