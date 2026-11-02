#!/usr/bin/env python3
"""
Échafaudeur d'API Backend (NestJS / Express / TypeScript).
Génère les DTOs, contrôleurs, services et entités avec validation stricte.
Usage:
    python api_scaffolder.py <resource_name> [--framework nestjs|express] [--dir <path>]
"""

import os
import sys
import argparse

def generate_nestjs_module(name, out_dir):
    pascal = "".join([part.capitalize() for part in name.split("_")])
    kebab = name.replace("_", "-")

    os.makedirs(os.path.join(out_dir, kebab, "dto"), exist_ok=True)

    # 1. DTO
    dto_content = f"""import {{ IsString, IsNotEmpty, IsOptional, MaxLength }} from 'class-validator';

export class Create{pascal}Dto {{
  @IsString()
  @IsNotEmpty()
  @MaxLength(255)
  title: string;

  @IsString()
  @IsOptional()
  description?: string;
}}

export class Update{pascal}Dto {{
  @IsString()
  @IsOptional()
  @MaxLength(255)
  title?: string;

  @IsString()
  @IsOptional()
  description?: string;
}}
"""
    with open(os.path.join(out_dir, kebab, "dto", f"create-{kebab}.dto.ts"), "w", encoding="utf-8") as f:
        f.write(dto_content)

    # 2. Service
    service_content = f"""import {{ Injectable, NotFoundException }} from '@nestjs/common';
import {{ PrismaService }} from '../prisma/prisma.service';
import {{ Create{pascal}Dto, Update{pascal}Dto }} from './dto/create-{kebab}.dto';

@Injectable()
export class {pascal}Service {{
  constructor(private readonly prisma: PrismaService) {{}}

  async findAll(page = 1, limit = 20) {{
    const skip = (page - 1) * limit;
    const [items, total] = await Promise.all([
      this.prisma.{kebab}.findMany({{
        skip,
        take: Math.min(limit, 100),
        orderBy: {{ createdAt: 'desc' }},
      }}),
      this.prisma.{kebab}.count(),
    ]);

    return {{
      data: items,
      meta: {{ total, page, limit, pages: Math.ceil(total / limit) }},
    }};
  }}

  async findOne(id: string) {{
    const item = await this.prisma.{kebab}.findUnique({{ where: {{ id }} }});
    if (!item) throw new NotFoundException(`Ressource ${{id}} introuvable`);
    return item;
  }}

  async create(dto: Create{pascal}Dto, userId: string) {{
    return this.prisma.{kebab}.create({{
      data: {{ ...dto, authorId: userId }},
    }});
  }}
}}
"""
    with open(os.path.join(out_dir, kebab, f"{kebab}.service.ts"), "w", encoding="utf-8") as f:
        f.write(service_content)

    # 3. Controller
    controller_content = f"""import {{ Controller, Get, Post, Body, Param, Query, UseGuards }} from '@nestjs/common';
import {{ {pascal}Service }} from './{kebab}.service';
import {{ Create{pascal}Dto }} from './dto/create-{kebab}.dto';
import {{ JwtAuthGuard }} from '../common/guards/jwt-auth.guard';
import {{ CurrentUser }} from '../common/decorators/current-user.decorator';

@Controller('api/v1/{kebab}')
export class {pascal}Controller {{
  constructor(private readonly service: {pascal}Service) {{}}

  @Get()
  async findAll(@Query('page') page = '1', @Query('limit') limit = '20') {{
    return this.service.findAll(+page, +limit);
  }}

  @Get(':id')
  async findOne(@Param('id') id: string) {{
    return this.service.findOne(id);
  }}

  @Post()
  @UseGuards(JwtAuthGuard)
  async create(@Body() dto: Create{pascal}Dto, @CurrentUser('id') userId: string) {{
    return this.service.create(dto, userId);
  }}
}}
"""
    with open(os.path.join(out_dir, kebab, f"{kebab}.controller.ts"), "w", encoding="utf-8") as f:
        f.write(controller_content)

    print(f"✅ Module NestJS '{kebab}' généré avec succès dans : {os.path.join(out_dir, kebab)}")

def generate_express_module(name, out_dir):
    kebab = name.replace("_", "-")
    os.makedirs(os.path.join(out_dir, kebab), exist_ok=True)

    route_content = f"""import {{ Router, Request, Response, NextFunction }} from 'express';
import {{ z }} from 'zod';

const router = Router();

const createSchema = z.object({{
  title: z.string().min(1).max(255),
  description: z.string().optional(),
}});

router.get('/', async (req: Request, res: Response, next: NextFunction) => {{
  try {{
    // Implémentation du service
    res.json({{ data: [], meta: {{ total: 0 }} }});
  }} catch (err) {{
    next(err);
  }}
}});

router.post('/', async (req: Request, res: Response, next: NextFunction) => {{
  try {{
    const parsed = createSchema.parse(req.body);
    // Création
    res.status(201).json({{ success: true, data: parsed }});
  }} catch (err) {{
    next(err);
  }}
}});

export default router;
"""
    with open(os.path.join(out_dir, kebab, "routes.ts"), "w", encoding="utf-8") as f:
        f.write(route_content)
    print(f"✅ Routeur Express '{kebab}' généré avec succès dans : {os.path.join(out_dir, kebab)}")

def main():
    parser = argparse.ArgumentParser(description="Échafaudeur d'API Backend Senior")
    parser.add_argument("name", help="Nom de la ressource (ex: articles, documents, users)")
    parser.add_argument("--framework", choices=["nestjs", "express"], default="nestjs", help="Framework cible")
    parser.add_argument("--dir", default="src/modules", help="Répertoire de sortie")
    args = parser.parse_args()

    if args.framework == "nestjs":
        generate_nestjs_module(args.name, args.dir)
    else:
        generate_express_module(args.name, args.dir)

if __name__ == "__main__":
    main()

