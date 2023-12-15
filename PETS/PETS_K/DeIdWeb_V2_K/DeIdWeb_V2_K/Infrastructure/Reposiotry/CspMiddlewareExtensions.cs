using Microsoft.AspNetCore.Builder;
using System;

namespace DeIdWeb_V2_K.Infrastructure.Reposiotry
{
    public static class CspMiddlewareExtensions
    {
        public static IApplicationBuilder UseCsp(this IApplicationBuilder app, CspOptions options)
        {
            return app.UseMiddleware<CspMiddleware>(options);
        }
        public static IApplicationBuilder UseCsp(this IApplicationBuilder app, Action<CspOptions> optionsDelegate)
        {
            var options = new CspOptions();
            optionsDelegate(options);
            return app.UseMiddleware<CspMiddleware>(options);
        }
    }
}
