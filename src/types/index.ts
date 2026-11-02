export type ContentStatus = 'BROUILLON' | 'EN_RELECTURE' | 'PUBLIE' | 'REJETE' | 'ARCHIVE';

export type ArticleCategory =
  | 'aeroport'
  | 'meteo'
  | 'social'
  | 'gouvernance'
  | 'cooperation'
  | 'publication';

export interface ArticleItem {
  id: string;
  slug: string;
  title: string;
  excerpt: string;
  coverImage: string;
  category: ArticleCategory;
  categoryLabel: string;
  publishedAt: string;
  readTimeMinutes: number;
  featured?: boolean;
}

export interface AirportSite {
  id: string;
  name: string;
  type: 'airport' | 'meteo';
  typeLabel: string;
  codeIcao: string;
  codeIata: string;
  status: string;
  piste: string;
  sslia: string;
  afisFreq: string;
  equipment: string;
  traffic: string;
  x: number;
  y: number;
}

