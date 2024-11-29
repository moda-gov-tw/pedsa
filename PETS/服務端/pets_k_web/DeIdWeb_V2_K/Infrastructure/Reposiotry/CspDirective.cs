using System.Collections.Generic;

namespace DeIdWeb_V2_K.Infrastructure.Reposiotry
{
    public class CspDirective
    {
        private readonly string _directive;

        internal CspDirective(string directive)
        {
            _directive = directive;
        }
        private List<string> _sources { get; set; } = new List<string>();
        public virtual CspDirective AllowAny() => Allow("*");
        public virtual CspDirective Disallow() => Allow("'none'");
        public virtual CspDirective AllowSelf() => Allow("'self'");
        public virtual CspDirective Allow(string source)
        {
            _sources.Add(source);
            return this;
        }
        public override string ToString() => _sources.Count > 0
            ? $"{_directive} {string.Join(" ", _sources)}; " : "";
    }
}
