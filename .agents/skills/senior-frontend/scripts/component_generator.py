#!/usr/bin/env python3
"""
Générateur de composants, hooks, tests et stories React / Next.js.
Usage:
    python component_generator.py <Name> [--type client|server|hook] [--dir <path>] [--with-test] [--with-story]
"""

import sys
import os
import argparse

def generate_client_component(name):
    return f"""'use client';

import React from 'react';
import {{ cn }} from '@/lib/utils';

export interface {name}Props extends React.HTMLAttributes<HTMLDivElement> {{
  children?: React.ReactNode;
}}

export function {name}({{ className, children, ...props }}: {name}Props) {{
  return (
    <div className={{cn('relative', className)}} {{...props}}>
      {{children}}
    </div>
  );
}}
"""

def generate_server_component(name):
    return f"""import React from 'react';
import {{ cn }} from '@/lib/utils';

export interface {name}Props {{
  className?: string;
  children?: React.ReactNode;
}}

export async function {name}({{ className, children }}: {name}Props) {{
  return (
    <section className={{cn('w-full', className)}}>
      {{children}}
    </section>
  );
}}
"""

def generate_hook(name):
    hook_name = name if name.startswith('use') else f'use{name}'
    return f"""import {{ useState, useEffect, useCallback }} from 'react';

export interface {hook_name}Options {{
  initialValue?: unknown;
}}

export function {hook_name}(options: {hook_name}Options = {{}}) {{
  const [value, setValue] = useState(options.initialValue);

  const reset = useCallback(() => {{
    setValue(options.initialValue);
  }}, [options.initialValue]);

  return {{
    value,
    setValue,
    reset,
  }};
}}
"""

def generate_test(name, comp_type):
    if comp_type == 'hook':
        hook_name = name if name.startswith('use') else f'use{name}'
        return f"""import {{ renderHook, act }} from '@testing-library/react';
import {{ describe, it, expect }} from 'vitest';
import {{ {hook_name} }} from './{hook_name}';

describe('{hook_name}', () => {{
  it('should initialize with initial value', () => {{
    const {{ result }} = renderHook(() => {hook_name}({{ initialValue: 'test' }}));
    expect(result.current.value).toBe('test');
  }});
}});
"""
    return f"""import {{ render, screen }} from '@testing-library/react';
import {{ describe, it, expect }} from 'vitest';
import {{ {name} }} from './{name}';

describe('{name}', () => {{
  it('should render children properly', () => {{
    render(<{name}>Test Content</{name}>);
    expect(screen.getByText('Test Content')).toBeInTheDocument();
  }});
}});
"""

def generate_story(name):
    return f"""import type {{ Meta, StoryObj }} from '@storybook/react';
import {{ {name} }} from './{name}';

const meta: Meta<typeof {name}> = {{
  title: 'Components/{name}',
  component: {name},
  parameters: {{
    layout: 'centered',
  }},
  tags: ['autodocs'],
}};

export default meta;
type Story = StoryObj<typeof {name}>;

export const Default: Story = {{
  args: {{
    children: '{name} Demo',
  }},
}};
"""

def main():
    parser = argparse.ArgumentParser(description="Générateur de composants React & Next.js")
    parser.add_argument("name", help="Nom du composant ou du hook")
    parser.add_argument("--type", choices=["client", "server", "hook"], default="client", help="Type d'élément")
    parser.add_argument("--dir", default="src/components", help="Répertoire cible")
    parser.add_argument("--with-test", action="store_true", help="Générer le fichier de test")
    parser.add_argument("--with-story", action="store_true", help="Générer le fichier Storybook")
    parser.add_argument("--flat", action="store_true", help="Ne pas créer de sous-dossier dédié")

    args = parser.parse_args()

    target_dir = args.dir if args.flat else os.path.join(args.dir, args.name)
    os.makedirs(target_dir, exist_ok=True)

    if args.type == "hook":
        filename = args.name if args.name.startswith('use') else f'use{args.name}'
        ext = ".ts"
        code = generate_hook(args.name)
    elif args.type == "server":
        filename = args.name
        ext = ".tsx"
        code = generate_server_component(args.name)
    else:
        filename = args.name
        ext = ".tsx"
        code = generate_client_component(args.name)

    main_file = os.path.join(target_dir, f"{filename}{ext}")
    with open(main_file, "w", encoding="utf-8") as f:
        f.write(code)
    print(f"✅ Créé : {main_file}")

    if args.with_test:
        test_file = os.path.join(target_dir, f"{filename}.test{ext}")
        with open(test_file, "w", encoding="utf-8") as f:
            f.write(generate_test(filename, args.type))
        print(f"✅ Créé : {test_file}")

    if args.with_story and args.type != "hook":
        story_file = os.path.join(target_dir, f"{filename}.stories.tsx")
        with open(story_file, "w", encoding="utf-8") as f:
            f.write(generate_story(filename))
        print(f"✅ Créé : {story_file}")

if __name__ == "__main__":
    main()

