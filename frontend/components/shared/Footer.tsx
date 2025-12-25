interface FooterLink {
  name: string;
  href: string;
}

interface FooterSection {
  title: string;
  links: FooterLink[];
}

const footerSections: FooterSection[] = [
  {
    title: 'Product',
    links: [
      { name: 'Features', href: '#features' },
      { name: 'Download', href: '/login' },
      { name: 'Roadmap', href: '#' },
      { name: 'Changelog', href: '#' },
    ],
  },
  {
    title: 'Community',
    links: [
      { name: 'Discord', href: '#' },
      { name: 'Blog', href: '#' },
      { name: 'Twitter', href: '#' },
      { name: 'Contact', href: '#' },
    ],
  },
  {
    title: 'Legal',
    links: [
      { name: 'Privacy Policy', href: '#' },
      { name: 'Terms of Service', href: '#' },
      { name: 'Content Dispute', href: '#' },
    ],
  },
];

export function Footer() {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="bg-zinc-900 dark:bg-black text-white pt-20 pb-10 border-t border-zinc-800">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-12 mb-16">
          <div className="col-span-1 md:col-span-1">
            <div className="flex items-center gap-2 mb-6">
              <span className="material-symbols-outlined text-2xl">auto_awesome</span>
              <span className="font-bold text-xl tracking-tight">Flow</span>
            </div>
            <p className="text-zinc-400 text-sm leading-relaxed">
              Your personalized productivity companion available 24/7. Get briefed on your emails, calendar, news, and priorities.
            </p>
          </div>
          {footerSections.map((section) => (
            <FooterColumn key={section.title} title={section.title} links={section.links} />
          ))}
        </div>
        <div className="border-t border-zinc-800 pt-8 flex flex-col md:flex-row justify-between items-center gap-4">
          <p className="text-zinc-500 text-xs">© {currentYear} Flow. All rights reserved.</p>
        </div>
      </div>
    </footer>
  );
}

function FooterColumn({ title, links }: FooterSection) {
  return (
    <div>
      <h4 className="font-bold text-sm uppercase tracking-wider text-zinc-500 mb-6">{title}</h4>
      <ul className="space-y-4">
        {links.map((link) => (
          <li key={link.name}>
            <a
              className="text-sm text-zinc-300 hover:text-white transition-colors"
              href={link.href}
            >
              {link.name}
            </a>
          </li>
        ))}
      </ul>
    </div>
  );
}
