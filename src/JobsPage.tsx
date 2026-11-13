import {Theme} from '@astryxdesign/core/theme';
import {Heading} from '@astryxdesign/core/Heading';
import {Text} from '@astryxdesign/core/Text';
import {Link} from '@astryxdesign/core/Link';
import {Table, proportional, pixel} from '@astryxdesign/core/Table';
import {VStack} from '@astryxdesign/core/VStack';
import {themes, defaultThemeSlug} from '../astryx-themes';
import {jobs, type Job} from './jobsData';

// One static page. Level is shown as LinkedIn reported it, because the list
// runs from internships to director; the location filter is injected after
// render by scripts/inject-location-filter.py because the renderer strips
// script.

const columns = [
  {
    key: 'title' as const,
    header: 'Role',
    width: proportional(2.4, {minWidth: 260}),
    // target="_blank" rather than Astryx's isExternalLink: that flag appends
    // "(opens in new tab)" screen-reader text, which the title cell's sort
    // script would then include in the sorted string. rel is set by hand so
    // no window.opener handle leaks to the posting.
    renderCell: (job: Job) => (
      <Link href={job.url} target="_blank" rel="noopener noreferrer">
        {job.title}
      </Link>
    ),
  },
  {
    key: 'company' as const,
    header: 'Company',
    width: proportional(1.3, {minWidth: 150}),
    renderCell: (job: Job) => <Text type="body">{job.company}</Text>,
  },
  {
    key: 'location' as const,
    header: 'Location',
    width: pixel(150),
    renderCell: (job: Job) => <Text type="body" color="secondary">{job.location}</Text>,
  },
  {
    key: 'level' as const,
    header: 'Level',
    width: pixel(140),
    renderCell: (job: Job) => <Text type="body" color="secondary">{job.level}</Text>,
  },
  {
    key: 'posted' as const,
    header: 'Posted',
    width: pixel(120),
    align: 'end' as const,
    renderCell: (job: Job) => (
      <Text type="body" color="secondary" hasTabularNumbers>
        {job.posted}
      </Text>
    ),
  },
];

export default function JobsPage({heading}: {heading: string}) {
  return (
    <Theme theme={themes[defaultThemeSlug]}>
      <VStack gap={4} padding={6}>
        <Heading level={1}>{heading}</Heading>
        <Table<Job>
          data={jobs}
          columns={columns}
          idKey="id"
          density="compact"
          dividers="rows"
          isStriped
          hasHover
        />
      </VStack>
    </Theme>
  );
}

export {jobs};
