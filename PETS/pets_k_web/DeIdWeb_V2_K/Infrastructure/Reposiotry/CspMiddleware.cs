using Microsoft.AspNetCore.Http;
using System.Text;
using System.Threading.Tasks;

namespace DeIdWeb_V2_K.Infrastructure.Reposiotry
{
    public class CspMiddleware
    {
        private readonly RequestDelegate _next;
        private readonly CspOptions _options;

        public CspMiddleware(RequestDelegate next, CspOptions options)
        {
            _next = next;
            _options = options;
        }

        private string Header => _options.ReadOnly
            ? "Content-Security-Policy-Report-Only" : "Content-Security-Policy";

        private string HeaderValue
        {
            get
            {
                var stringBuilder = new StringBuilder();
                stringBuilder.Append(_options.Defaults);
                stringBuilder.Append(_options.Connects);
                stringBuilder.Append(_options.Fonts);
                stringBuilder.Append(_options.Frames);
                stringBuilder.Append(_options.Images);
                stringBuilder.Append(_options.Media);
                stringBuilder.Append(_options.Objects);
                stringBuilder.Append(_options.Scripts);
                stringBuilder.Append(_options.Styles);
                if (!string.IsNullOrEmpty(_options.ReportURL))
                {
                    stringBuilder.Append($"report-uri {_options.ReportURL};");
                }
                stringBuilder.Append(_options.FrameAncestors);
                return stringBuilder.ToString();
            }
        }

        public async Task Invoke(HttpContext context)
        {
            context.Response.Headers.Add(Header, HeaderValue);
            if (!string.IsNullOrEmpty(_options.FrameAncestors.XFrameOptions))
            {
                context.Response.Headers.Add("X-Frame-Options", _options.FrameAncestors.XFrameOptions);
            }
            await _next(context);
        }
    }
}
