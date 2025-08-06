import numpy as np
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection

def draw_model_curves(ax, xqulr, yqulr, model_data_grouped, shock_data_grouped, precursor_data_grouped, vmin, vmax, vstep, independent):

    last_lc = None

    if independent:

        for i, (shck_data, prec_data) in enumerate(zip(shock_data_grouped, precursor_data_grouped)):
            
            # Load model data as quantity or line ratio
            if xqulr == 'Line Ratio':
                x_id = 1
            else:
                x_id = 3
            if yqulr == 'Line Ratio':
                y_id = 2
            else:
                y_id = 4
            shck_xdata = shck_data.iloc[:, x_id]
            shck_xlab = shck_data.columns[x_id]
            shck_ydata = shck_data.iloc[:, y_id]
            shck_ylab = shck_data.columns[y_id]
            shck_vels = shck_data.iloc[:, 0].values
        
            prec_xdata = prec_data.iloc[:, x_id]
            prec_xlab = prec_data.columns[x_id]
            prec_ydata = prec_data.iloc[:, y_id]
            prec_ylab = prec_data.columns[y_id]

            # Convert x_data and y_data into a sequence of line segments
            shck_points = np.array([shck_xdata, shck_ydata]).T.reshape(-1, 1, 2)
            shck_segments = np.concatenate([shck_points[:-1], shck_points[1:]], axis=1)

            prec_points = np.array([prec_xdata, prec_ydata]).T.reshape(-1, 1, 2)
            prec_segments = np.concatenate([prec_points[:-1], prec_points[1:]], axis=1)

            # Create a LineCollection with colors based on 'shocks'
            shck_lc = LineCollection(shck_segments, cmap='viridis', norm=plt.Normalize(vmin, vmax))
            prec_lc = LineCollection(prec_segments, cmap='viridis', norm=plt.Normalize(vmin, vmax))
            shck_lc.set_array(shck_vels)
            prec_lc.set_array(shck_vels)
            ax.add_collection(shck_lc)
            ax.add_collection(prec_lc)
            
            last_lc = shck_lc

            # Add axis labels
            if i == 0:
                ax.set_xlabel(shck_xlab, size=18)
                ax.set_ylabel(shck_ylab, size=18)

            # Add gray connection to previous dataset
            if i > 0:
                # Access previous model data
                prev_shck_xdata = shock_data_grouped[i - 1].iloc[:, x_id].values
                prev_shck_ydata = shock_data_grouped[i - 1].iloc[:, y_id].values
                prev_prec_xdata = precursor_data_grouped[i - 1].iloc[:, x_id].values
                prev_prec_ydata = precursor_data_grouped[i - 1].iloc[:, y_id].values

                ax.plot((shck_xdata, prev_shck_xdata), (shck_ydata, prev_shck_ydata), color='gray', alpha=0.5)
                ax.plot((prec_xdata, prev_prec_xdata), (prec_ydata, prev_prec_ydata), color='gray', alpha=0.5)

    else:
        # Loop over each magnetic field group
        for i, model_data in enumerate(model_data_grouped):

            # Load model data as quantity or line ratio
            if xqulr == 'Line Ratio':
                x_id = 1
            else:
                x_id = 3
            if yqulr == 'Line Ratio':
                y_id = 2
            else:
                y_id = 4
            model_xdata = model_data.iloc[:, x_id]
            model_xlab = model_data.columns[x_id]
            model_ydata = model_data.iloc[:, y_id]
            model_ylab = model_data.columns[y_id]
            shck_vels = model_data.iloc[:, 0].values

            # TODO: Add in changes to shock velocities with vstep

            # Convert x_data and y_data into a sequence of line segments
            points = np.array([model_xdata, model_ydata]).T.reshape(-1, 1, 2)
            segments = np.concatenate([points[:-1], points[1:]], axis=1)

            # Create a LineCollection with colors based on 'shocks'
            shck_lc = LineCollection(segments, cmap='viridis', norm=plt.Normalize(vmin, vmax))
            shck_lc.set_array(shck_vels)
            ax.add_collection(shck_lc)
            last_lc = shck_lc

            # Add axis labels
            if i == 0:
                ax.set_xlabel(model_xlab)
                ax.set_ylabel(model_ylab)

            # Add gray connection to previous dataset
            if i > 0:
                # Access previous model data
                prev_model_xdata = model_data_grouped[i - 1].iloc[:, x_id].values
                prev_model_ydata = model_data_grouped[i - 1].iloc[:, y_id].values
                ax.plot((model_xdata, prev_model_xdata), (model_ydata, prev_model_ydata), color='gray', alpha=0.5)

    return last_lc

def draw_fits_points(ax, fits_x, fits_y, fits_z, use_fits_mask, fits_mask, vmin, vmax):
    """
    Plot FITS-derived data points on the given Axes.

    Parameters:
    - ax: matplotlib Axes object to draw on
    - fits_x, fits_y, fits_z: 1D arrays of same length, for scatter plot
    - vmin, vmax: numeric, for color normalization
    """

    # Apply mask if uploaded
    if use_fits_mask:
        fits_x = fits_x[~fits_mask]
        fits_y = fits_y[~fits_mask]
        fits_z = fits_z[~fits_mask]

    # Plot (masked) data in scatter plot
    ax.scatter(
        fits_x,
        fits_y,
        c=fits_z,
        cmap='viridis',
        vmin=vmin,
        vmax=vmax,
        marker='.',
        alpha=0.5
    )

def finalize_plot(fig, ax, lc, x_lab, y_lab, abun, dens):
    """
    Add colorbar, labels, title, and log scales to the plot.

    Parameters:
    - fig: matplotlib Figure object
    - ax: matplotlib Axes object
    - lc: last LineCollection returned by draw_model_curves (for colorbar reference)
    - x_lab, y_lab: string labels for axes
    - abun: selected abundance (string)
    - dens: selected density (string)
    """
    cbar = fig.colorbar(lc)
    cbar.set_label('Shock velocity / km s$^{-1}$', size=18)
    cbar.ax.tick_params(labelsize=12) 
    # ax.set_title(f'{y_lab} against {x_lab}\nAbundance = {abun}; Density = {dens} cm$^{{-3}}$', size=18)
    ax.tick_params(axis="both", labelsize=12)
    ax.set_xscale('log')
    ax.set_yscale('log')

    return cbar