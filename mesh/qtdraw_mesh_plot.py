#!/usr/bin/env python

import altair as alt
import click
import pandas as pd

def mesh_read(input_filename: str) -> pd.DataFrame:
    df = pd.read_csv(input_filename, sep='\t', usecols=('x','y','z'))
    print(f"found a mesh in '{input_filename}' of size {df.size} with {df.shape[0]} rows and {df.shape[1]} cols")
    return df


@click.command()
@click.option('--output_filename', type=str, default='qtdraw_mesh.png')
@click.option('--input_filename', type=str, default='qtdraw_mesh.tsv')
def qtdraw_mesh_plot(output_filename: str, input_filename: str):
    mesh = mesh_read(input_filename)

    chart = alt.Chart(mesh).mark_rect().encode(
        x='x:O',
        y='y:O',
        color='z:Q'
    )
    chart.save(output_filename)

if __name__ == '__main__':
    qtdraw_mesh_plot()
