using Dapper;
using DeIdWeb_V2.Models;
using log4net;
using Microsoft.Extensions.Configuration;
using MySql.Data.MySqlClient;
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;

namespace DeIdWeb_V2.Infrastructure.Service
{

    public class SystemLog_Service
    {
        public static IConfiguration Configuration { get; set; }
        private ILog log = LogManager.GetLogger(Startup.repository.Name, typeof(SystemLog_Service));

        public SystemLog_Service()
        {
            var builder = new ConfigurationBuilder()
            .SetBasePath(Directory.GetCurrentDirectory())
            .AddJsonFile("appsettings.json");
            Configuration = builder.Build();
        }
    }
}
