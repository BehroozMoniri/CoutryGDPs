from django.shortcuts import render
from django.db.models import Max, Min
from gdp.models import GDP
import math
from bokeh.embed import components
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource , NumeralTickFormatter, HoverTool
# Create your views here.


def index(request):
    # get the year from GET request, or default to the maximum year in the data
    max_year = GDP.objects.aggregate(max_year=Max('year'))['max_year']
    # the above line returns a dictionary with a key that we named as max_year to get the 
    # actual number out we use the ['max_year'] key at the end of the line 
    year = request.GET.get('year', max_year)
    # get the number of countries to show in the bar chart - default to 10
    count = int(request.GET.get('count',10 ))
    # height = int(request.GET.get('height-slider',700 ))
    # width =  int(request.GET.get('width-slider',700 ))
    # extract data for that year for top N
    gdps = GDP.objects.filter(year=year).order_by('gdp').reverse()[:count]
    
    country_names = [ d.country for d in gdps]
    country_gdps = [d.gdp for d in gdps ]  # get
    
    
    cds = ColumnDataSource(data=dict(country_names = country_names , country_gdps=country_gdps ))
    
    fig = figure(x_range=country_names, width=700, height=700 , title=f"Top {count} GDPs ({year})")
    fig.title.align = 'center'
    fig.title.text_font_size = '1.5em'
    fig.yaxis[0].formatter = NumeralTickFormatter(format="$0.0a")
    fig.xaxis.major_label_orientation = math.pi / 4
    
    fig.vbar(x='country_names', top ="country_gdps", width=0.8,  source=cds)
    tooltips = [ ('Country','@country_names'),
                ('GDP', '@country_gdps{,}')]
    
    fig.add_tools(HoverTool(tooltips=tooltips))
    script, div = components(fig)
    max_year = GDP.objects.aggregate(max_yr=Max('year'))['max_yr']
    min_year = GDP.objects.aggregate(min_yr=Min('year'))['min_yr']
    year = request.GET.get('year', max_year)
    context = {
        'script': script, 
        'div': div,
        'years': range(min_year , max_year +1),  # +1 to include the final year!
        'year_selected': year,  # the year for which we currently show data
        'count': count  # the number of bars to show
        # 'height' : height,
        # 'width': width 
    }
    if request.htmx:
        return render(request, 'partials/gdp-bar.html', context)
                
    return render(request, 'index.html', context )

def line(request):
    countries = GDP.objects.values_list('country', flat=True).distinct()
    country = request.GET.get('country', 'Germany')
 
    year_data = []
    gdp_data= []
    
    # c= ['Germany', 'China', 'France']
    # for country in c:
    #         gdpss = GDP.objects.filter(country=country).order_by('year') #.reverse()[:count]
    #         year_data.append([d.year for d in gdps])
    #         gdp_data.append([d.gdp for d in gdpss])  
            
    gdps = GDP.objects.filter(country=country).order_by('year') #.reverse()[:count]
    country_years = [ d.year for d in gdps]
    country_gdps = [d.gdp for d in gdps ]  # get
    
    # year_data.append([d.year for d in gdpss])
    # gdp_data.append([d.gdp for d in gdpss])  
    
    cds = ColumnDataSource(data=dict(country_years = country_years , country_gdps=country_gdps ))
   
    fig = figure( width=500, height=500 , title=f"{country} GDP") #x_range=country_years,
    fig.title.align = 'center'
    fig.title.text_font_size = '1.5em'
    fig.yaxis[0].formatter = NumeralTickFormatter(format="$0.0a")
    fig.xaxis.major_label_orientation = math.pi / 4
    
    fig.line(x='country_years', y ="country_gdps", line_width=1.5,  source=cds)
  
    tooltips = [        ('GDP', '@country_gdps{,}')]
    fig.add_tools(HoverTool(tooltips=tooltips))
    script, div = components(fig)
     
    context = {
        'script': script, 
        'div': div,
       # 'years': range(min_year , max_year +1),  # +1 to include the final year!
        'countries': countries,   
        'country': country  
    }
    if request.htmx:
        return render(request, 'partials/gdp-bar.html', context)
                
    return render(request, 'line.html', context )

def multiline(request):
    countries = GDP.objects.values_list('country', flat=True).distinct()
    country1 = request.GET.get('country1', 'Germany')
    country2 = request.GET.get('country2', 'France')
    country3 = request.GET.get('country3', 'United Kingdom')
    year_data = []
    gdp_data= []
    
    c= [country1, country2 , country3]
    for country in c:
            gdpss = GDP.objects.filter(country=country).order_by('year') #.reverse()[:count]
            year_data.append([d.year for d in gdpss])
            gdp_data.append([d.gdp for d in gdpss])  
            
    
    cdss = ColumnDataSource(data=dict(country_years = year_data ,
                                      country_gdps=  gdp_data ,
                                      names = c,
                                      colors = ['red', 'blue', 'green']           ))
    names = [" " + country for country in c]
    
    fig = figure( width=500, height=500 , title=f"{names} GDP") #x_range=country_years,
    fig.title.align = 'center'
    fig.title.text_font_size = '1.5em'
    fig.yaxis[0].formatter = NumeralTickFormatter(format="$0.0a")
    fig.xaxis.major_label_orientation = math.pi / 4
     
    fig.multi_line(source=cdss,xs='country_years', ys ="country_gdps", line_width=1.5,
                   legend_group='names',line_color='colors' )
    fig.legend.location = 'top_left'
    tooltips = [        ('GDP', '@country_gdps{,}')]
    fig.add_tools(HoverTool(tooltips=tooltips))
    script, div = components(fig)
     
    context = {
        'script': script, 
        'div': div,
       # 'years': range(min_year , max_year +1),  # +1 to include the final year!
        'countries': countries,   
        'country1': country1  ,
        'country2': country2  ,
        'country3': country3  
    }
    if request.htmx:
        return render(request, 'partials/gdp-bar.html', context)
                
    return render(request, 'multiline.html', context )