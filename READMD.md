<h1>Muchview</h1>
<p>
    A Web Crawler project using Python.
</p>

<pre>
from muchview import MuchViewEngine

obj = MuchViewEngine('http://www.adorama.com/Reviews/pwr/product-reviews/c/index.html')
obj.source_name = 'adorama.com'
obj.language = 'en'
obj.en = 'utf8'
obj.short_url = 'http://www.adorama.com/Reviews/pwr/'
obj.category_by_this_agent = 'camera, video'
obj.create_agent()
obj.cates('//div[@class="prMiniSiteCategoryListing"]/a','text()', '@href',process_sub_category=False,replace_url_1=True)

obj.agent_items('//div[@class="prMiniSiteProductListingTitle"]/a','text()', '@href', \
                nextpage=False,  \
                replace_url_1=True, \
                attrs=dict(
                            logo = '//img[@class="prMiniSiteProductImage"]/@src',
                            title = '//title/text()',
                            images = dict(path='//img[@class="prMiniSiteProductImage"]',key='@alt', value='@src'),
                            desc = '//div[@id="prMiniSiteProductDescription"]/descendant::text()',
                            cates = '//span[@class="prMiniSiteProductAreaValue"]/descendant::text()',
                            spec = dict(path='//div[@class="prReviewPoints"]/div/div[@class="prSummaryKey"]',key='text()',value='following::div[@class="prSummaryValue"]/text()'),
                            rating = '//div[@class="prSummaryAverageRatingDecimal"]/text()',
                            user_review = dict( path='//div[@id="prMiniSiteIndividualReviews"]/div[@class="prReviewWrap "]', 
                            author='div[@class="prReviewAuthor"]/span[@class="prReviewAuthorLocation"]/span/text()',
                            author_comment='div[@class="prReviewText"]/p[@class="prComments"]/descendant::text()',
                            review_datetime='div[@class="prReviewAuthor"]/span[@class="prReviewAuthorDate"]/span/text()',
                            pros_path='div[@class="prReviewPoints"]/div/div[@class="prReviewKey"]',
                            pros_key='text()',
                            pros_value='following::div[@class="prReviewValue"][1]/text()')
                            )
                )

obj.cursor.close()
obj.conn.close()

</pre>